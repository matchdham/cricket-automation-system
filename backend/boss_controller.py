# ============================================
# FILE: boss_controller.py
# PURPOSE: Boss panel - Admin/Worker management
# ============================================

from database import get_db_connection, log_error, fetch_one, fetch_all, execute_query
from auth import hash_password
import sqlite3
from datetime import datetime

class BossController:
    """Boss (Super Admin) operations"""
    
    def __init__(self):
        pass
    
    def create_admin(self, username, password, created_by_boss_id):
        """
        Admin user बनाओ (Boss की तरफ से)
        
        PARAMS:
            username: Admin का username
            password: Admin का password
            created_by_boss_id: Boss की ID
        
        RETURN:
            dict: {success, user_id, message}
        """
        try:
            # Username already exists check करो
            existing_user = fetch_one('SELECT id FROM users WHERE username = ?', (username,))
            if existing_user:
                return {'success': False, 'message': 'Username already exists'}
            
            # Password hash करो
            password_hash = hash_password(password)
            
            # Database में insert करो
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, created_by)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, 'admin', created_by_boss_id))
            
            user_id = cursor.lastrowid
            
            # Settings भी बनाओ
            cursor.execute('''
                INSERT INTO settings (admin_id, text_bold)
                VALUES (?, 1)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Audit log
            self.add_audit_log(created_by_boss_id, 'created_admin', user_id, f'Created admin: {username}')
            
            log_error('success', f'Admin created: {username}')
            
            return {
                'success': True,
                'user_id': user_id,
                'message': f'Admin {username} created'
            }
        
        except Exception as e:
            log_error('api_error', 'Create admin failed', str(e))
            return {'success': False, 'message': str(e)}
    
    def delete_admin(self, admin_id, boss_id):
        """
        Admin को delete करो
        Admin के सभी workers को दूसरे admin को transfer करो
        
        PARAMS:
            admin_id: Delete होने वाले admin की ID
            boss_id: Boss की ID (who is deleting)
        
        RETURN:
            dict: {success, message}
        """
        try:
            # Admin को verify करो
            admin = fetch_one('SELECT id FROM users WHERE id = ? AND role = "admin"', (admin_id,))
            if not admin:
                return {'success': False, 'message': 'Admin not found'}
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Admin के workers को खोजो
            cursor.execute('SELECT id FROM users WHERE parent_admin_id = ?', (admin_id,))
            workers = cursor.fetchall()
            
            if workers:
                # दूसरे admin को खोजो
                cursor.execute('SELECT id FROM users WHERE role = "admin" AND id != ? LIMIT 1', (admin_id,))
                other_admin = cursor.fetchone()
                
                if other_admin:
                    # सभी workers को transfer करो
                    for worker in workers:
                        cursor.execute('''
                            UPDATE users 
                            SET parent_admin_id = ?
                            WHERE id = ?
                        ''', (other_admin['id'], worker['id']))
                    
                    conn.commit()
            
            # Admin को delete करो
            cursor.execute('DELETE FROM users WHERE id = ?', (admin_id,))
            
            # Settings भी delete करो
            cursor.execute('DELETE FROM settings WHERE admin_id = ?', (admin_id,))
            
            conn.commit()
            conn.close()
            
            # Audit log
            self.add_audit_log(boss_id, 'deleted_admin', admin_id, f'Deleted admin ID: {admin_id}')
            
            log_error('success', f'Admin deleted: {admin_id}')
            
            return {
                'success': True,
                'message': f'Admin deleted. Workers transferred to another admin.'
            }
        
        except Exception as e:
            log_error('api_error', 'Delete admin failed', str(e))
            return {'success': False, 'message': str(e)}
    
    def get_all_users(self):
        """सभी users get करो (Hierarchy के साथ)"""
        try:
            # सभी admins
            admins = fetch_all('SELECT id, username, role, created_at FROM users WHERE role = "admin"')
            
            users_hierarchy = []
            
            for admin in admins:
                # Admin के सभी workers
                workers = fetch_all(
                    'SELECT id, username, role, created_at FROM users WHERE parent_admin_id = ?',
                    (admin['id'],)
                )
                
                users_hierarchy.append({
                    'admin': {
                        'id': admin['id'],
                        'username': admin['username'],
                        'role': admin['role'],
                        'created_at': admin['created_at']
                    },
                    'workers': workers
                })
            
            return {
                'success': True,
                'users': users_hierarchy
            }
        
        except Exception as e:
            log_error('api_error', 'Get users failed', str(e))
            return {'success': False, 'message': str(e)}
    
    def view_audit_logs(self, limit=100):
        """Boss के सभी actions का log देखो"""
        try:
            logs = fetch_all('''
                SELECT boss_id, action, affected_user_id, details, timestamp
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            return {
                'success': True,
                'logs': logs
            }
        
        except Exception as e:
            log_error('api_error', 'Get audit logs failed', str(e))
            return {'success': False, 'message': str(e)}
    
    def add_audit_log(self, boss_id, action, affected_user_id, details):
        """Audit log add करो"""
        try:
            execute_query('''
                INSERT INTO audit_logs (boss_id, action, affected_user_id, details)
                VALUES (?, ?, ?, ?)
            ''', (boss_id, action, affected_user_id, details))
            
            return True
        
        except Exception as e:
            log_error('api_error', 'Add audit log failed', str(e))
            return False
    
    def get_dashboard_overview(self):
        """Boss dashboard के लिए overview data"""
        try:
            # कुल users
            cursor = get_db_connection().cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
            admin_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = "worker"')
            worker_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM posts')
            total_posts = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(total_images_posted) FROM lifecycle_counter')
            total_posted = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            return {
                'success': True,
                'admin_count': admin_count,
                'worker_count': worker_count,
                'total_posts': total_posts,
                'total_posted': total_posted
            }
        
        except Exception as e:
            log_error('api_error', 'Dashboard overview failed', str(e))
            return {'success': False, 'message': str(e)}
    
    def reset_user_password(self, user_id, new_password, boss_id):
        """किसी user का password reset करो"""
        try:
            # User को verify करो
            user = fetch_one('SELECT id FROM users WHERE id = ?', (user_id,))
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Password hash करो
            password_hash = hash_password(new_password)
            
            # Update करो
            execute_query('''
                UPDATE users 
                SET password_hash = ?
                WHERE id = ?
            ''', (password_hash, user_id))
            
            # Audit log
            self.add_audit_log(boss_id, 'reset_password', user_id, f'Reset password for user ID: {user_id}')
            
            log_error('success', f'Password reset: {user_id}')
            
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
        
        except Exception as e:
            log_error('api_error', 'Reset password failed', str(e))
            return {'success': False, 'message': str(e)}
    
    def toggle_user_status(self, user_id, status, boss_id):
        """User को active/inactive करो"""
        try:
            if status not in ['active', 'inactive']:
                return {'success': False, 'message': 'Invalid status'}
            
            execute_query('''
                UPDATE users 
                SET status = ?
                WHERE id = ?
            ''', (status, user_id))
            
            self.add_audit_log(boss_id, f'set_status_{status}', user_id, f'Changed status to {status}')
            
            log_error('success', f'User status changed: {user_id}')
            
            return {
                'success': True,
                'message': f'User status changed to {status}'
            }
        
        except Exception as e:
            log_error('api_error', 'Toggle user status failed', str(e))
            return {'success': False, 'message': str(e)}

# Global instance
boss_controller = BossController()

def create_admin(username, password, boss_id):
    """Admin create करो"""
    return boss_controller.create_admin(username, password, boss_id)

def delete_admin(admin_id, boss_id):
    """Admin delete करो"""
    return boss_controller.delete_admin(admin_id, boss_id)

def get_users():
    """सभी users देखो"""
    return boss_controller.get_all_users()

def view_logs(limit=100):
    """Audit logs देखो"""
    return boss_controller.view_audit_logs(limit)

def dashboard_overview():
    """Dashboard overview"""
    return boss_controller.get_dashboard_overview()

def reset_password(user_id, password, boss_id):
    """Password reset करो"""
    return boss_controller.reset_user_password(user_id, password, boss_id)

def toggle_status(user_id, status, boss_id):
    """Status toggle करो"""
    return boss_controller.toggle_user_status(user_id, status, boss_id)