from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models.document_model import DocumentModel
from models.notification_model import NotificationModel
from functools import wraps
import io

document_bp = Blueprint('document', __name__)

def login_required(f):
    """Decorator to require login for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Veuillez vous connecter pour accéder à cette page.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def document_access_required(f):
    """Decorator to require document access verification."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Veuillez vous connecter pour accéder à cette page.", "danger")
            return redirect(url_for('auth.login'))
        if not session.get('document_access_verified'):
            flash("Veuillez vérifier votre clé d'accès pour accéder à vos documents.", "warning")
            return redirect(url_for('document.request_access'))
        return f(*args, **kwargs)
    return decorated_function


@document_bp.route('/mes-documents/request-access', methods=['GET', 'POST'])
@login_required
def request_access():
    """Request access to Mes Documents - generates and sends access key via notification."""
    user_email = session['user']['email']
    
    if request.method == 'POST':
        # Generate access key and send notification
        access_key = DocumentModel.create_access_key_for_user(user_email)
        
        if access_key:
            # Create a notification with the access key
            create_document_access_notification(user_email, access_key)
            flash("Une clé d'accès a été envoyée dans vos notifications.", "success")
            return redirect(url_for('document.verify_access'))
        else:
            flash("Erreur lors de la génération de la clé d'accès.", "danger")
    
    return render_template('document_request_access.html')


@document_bp.route('/mes-documents/verify-access', methods=['GET', 'POST'])
@login_required
def verify_access():
    """Verify the access key to access Mes Documents."""
    user_email = session['user']['email']
    
    if request.method == 'POST':
        access_key = request.form.get('access_key', '').strip()
        
        if DocumentModel.verify_access_key(user_email, access_key):
            session['document_access_verified'] = True
            flash("Accès vérifié avec succès. Bienvenue dans Mes Documents!", "success")
            return redirect(url_for('document.list_documents'))
        else:
            flash("Clé d'accès invalide ou expirée. Veuillez demander une nouvelle clé.", "danger")
            return redirect(url_for('document.request_access'))
    
    return render_template('document_verify_access.html')


@document_bp.route('/mes-documents')
@document_access_required
def list_documents():
    """List all documents for the current user."""
    user_email = session['user']['email']
    documents = DocumentModel.get_user_documents(user_email)
    return render_template('document_list.html', documents=documents)


@document_bp.route('/mes-documents/upload', methods=['GET', 'POST'])
@document_access_required
def upload_document():
    """Upload a new document."""
    if request.method == 'POST':
        user_email = session['user']['email']
        
        if 'file' not in request.files:
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(request.url)
        
        file = request.files['file']
        description = request.form.get('description', '')
        
        if file.filename == '':
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(request.url)
        
        if file:
            filename = file.filename
            file_content = file.read()
            file_type = file.content_type or 'application/octet-stream'
            
            success, message, doc_id = DocumentModel.upload_document(
                user_email, filename, file_content, file_type, description
            )
            
            if success:
                flash(message, "success")
                return redirect(url_for('document.list_documents'))
            else:
                flash(message, "danger")
    
    return render_template('document_upload.html')


@document_bp.route('/mes-documents/view/<document_id>')
@document_access_required
def view_document(document_id):
    """View a specific document."""
    user_email = session['user']['email']
    document = DocumentModel.get_document_by_id(document_id, user_email)
    
    if document:
        return render_template('document_view.html', document=document)
    else:
        flash("Document non trouvé ou vous n'avez pas la permission de le voir.", "danger")
        return redirect(url_for('document.list_documents'))


@document_bp.route('/mes-documents/download/<document_id>')
@document_access_required
def download_document(document_id):
    """Download a document."""
    user_email = session['user']['email']
    document = DocumentModel.get_document_by_id(document_id, user_email)
    
    if document and 'file_content_decoded' in document:
        return send_file(
            io.BytesIO(document['file_content_decoded']),
            download_name=document['filename'],
            as_attachment=True,
            mimetype=document.get('file_type', 'application/octet-stream')
        )
    else:
        flash("Document non trouvé ou vous n'avez pas la permission de le télécharger.", "danger")
        return redirect(url_for('document.list_documents'))


@document_bp.route('/mes-documents/delete/<document_id>', methods=['POST'])
@document_access_required
def delete_document(document_id):
    """Delete a document."""
    user_email = session['user']['email']
    success, message = DocumentModel.delete_document(document_id, user_email)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for('document.list_documents'))


@document_bp.route('/mes-documents/logout')
@login_required
def logout_documents():
    """Logout from document access (requires re-verification)."""
    session.pop('document_access_verified', None)
    flash("Vous avez été déconnecté de Mes Documents.", "info")
    return redirect(url_for('main.dashboard'))




def create_document_access_notification(user_email, access_key):
    """
    Create a notification for document access with the access key.
    
    Args:
        user_email (str): Email of the user.
        access_key (str): The generated access key.
    """
    from config.mongo_client import db
    from datetime import datetime
    
    try:
        notification = {
            "sender_email": "system@mapen.app",
            "receiver_email": user_email,
            "notification_type": "document_access_key",
            "message": f"Votre clé pour aller dans Mes documents est : {access_key}",
            "key_used": access_key[::-1],  # Store reversed for consistency
            "timestamp": datetime.now(),
            "is_read": False
        }
        db.notifications.insert_one(notification)
        return True
    except Exception as e:
        print(f"Error creating document access notification: {str(e)}")
        return False
