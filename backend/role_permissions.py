# ============================================
# FILE: role_permissions.py
# PURPOSE: Role-based access control
# ============================================

from config import config
from database import log_error, fetch_one

class RolePermissions:
    """Role-based permissions check करो"""
    
    def __init__(self):
        self.permissions = {
            'boss': {
                'create_admin': True,
                'delete_admin': True,
                'manage_workers': True,
                'override_settings': True,
                'view_audit_logs': True,
                'reset_password': True,
                'create_post': True,
                'edit_post': True,
                'delete_post': True,
                'upload_player': True,
                'delete_player': True,
                'upload_background': True,
                'upload_sponsor': True,
                'toggle_settings': True,
                'view_dashboard': True,
                'view_health': True,
                'auto_track': True
            },
            'admin': {
                'create_admin': False,
                'delete_admin': False,
                'manage_workers': True,
                'override_settings': False,
                'view_audit_logs': False,
                'reset_password': False,
                'create_post': True,
                'edit_post': True,
                'delete_post': False,
                'upload_player': True,
                'delete_player': True,
                'upload_background': True,
                'upload_sponsor': True,
                'toggle_settings': True,
                'view_dashboard': True,
                'view_health': True,
                'auto_track': False
            },
            'worker': {
                'create_admin': False,
                'delete_admin': False,
                'manage_workers': False,
                'override_settings': False,
                'view_audit_logs': False,
                'reset_password': False,
                'create_post': True,
                'edit_post': config.WORKER_CAN_EDIT_CAPTION,
                'delete_post': False,
                'upload_player': config.WORKER_CAN_UPLOAD_PLAYER,
                'delete_player': False,
                'upload_background': False,
                'upload_sponsor': False,
                'toggle_settings': False,
                'view_dashboard': True,
                'view_health': config.WORKER_CAN_VIEW_HEALTH,
                'auto_track': False
            }
        }
    
    def check_permission(self, user_role, permission):
        """
        Check करो कि user को यह permission है या नहीं
        
        PARAMS:
            user_role: 'boss', 'admin', 'worker'
            permission: 'create_post', 'delete_admin', etc
        
        RETURN:
            bool: True/False
        """
        try:
            if user_role not in self.permissions:
                log_error('permission_error', f'Invalid role: {user_role}')
                return False
            
            if permission not in self.permissions[user_role]:
                log_error('permission_error', f'Invalid permission: {permission}')
                return False
            
            return self.permissions[user_role][permission]
        
        except Exception as e:
            log_error('api_error', 'Permission check error', str(e))
            return False
    
    def get_user_permissions(self, user_role):
        """किसी role के सभी permissions लो"""
        try:
            if user_role not in self.permissions:
                return []
            
            return self.permissions[user_role]
        
        except Exception as e:
            log_error('api_error', 'Get permissions error', str(e))
            return {}
    
    def has_multiple_permissions(self, user_role, permissions_list):
        """
        Check करो कि user के पास सभी permissions हैं
        
        PARAMS:
            user_role: 'admin'
            permissions_list: ['create_post', 'upload_player']
        
        RETURN:
            bool: True if has all, False if missing any
        """
        try:
            for perm in permissions_list:
                if not self.check_permission(user_role, perm):
                    return False
            
            return True
        
        except Exception as e:
            log_error('api_error', 'Multiple permissions check error', str(e))
            return False
    
    def has_any_permission(self, user_role, permissions_list):
        """
        Check करो कि user के पास कम से कम एक permission है
        
        PARAMS:
            user_role: 'admin'
            permissions_list: ['delete_admin', 'reset_password']
        
        RETURN:
            bool: True if has any, False if has none
        """
        try:
            for perm in permissions_list:
                if self.check_permission(user_role, perm):
                    return True
            
            return False
        
        except Exception as e:
            log_error('api_error', 'Any permission check error', str(e))
            return False
    
    def get_accessible_endpoints(self, user_role):
        """किसी role के लिए सभी accessible endpoints"""
        try:
            accessible = []
            
            for endpoint, allowed in self.permissions[user_role].items():
                if allowed:
                    accessible.append(endpoint)
            
            return accessible
        
        except Exception as e:
            log_error('api_error', 'Get endpoints error', str(e))
            return []
    
    def get_role_level(self, user_role):
        """Role का level get करो (hierarchy)"""
        try:
            role_levels = {
                'boss': 3,
                'admin': 2,
                'worker': 1
            }
            
            return role_levels.get(user_role, 0)
        
        except Exception as e:
            log_error('api_error', 'Get role level error', str(e))
            return 0
    
    def is_higher_role(self, role1, role2):
        """
        Check करो कि role1 > role2 है
        
        PARAMS:
            role1: 'admin'
            role2: 'worker'
        
        RETURN:
            bool: True if role1 > role2
        """
        try:
            level1 = self.get_role_level(role1)
            level2 = self.get_role_level(role2)
            
            return level1 > level2
        
        except Exception as e:
            log_error('api_error', 'Role comparison error', str(e))
            return False

# Global instance
role_permissions = RolePermissions()

def check_permission(user_role, permission):
    """Permission check करो"""
    return role_permissions.check_permission(user_role, permission)

def get_permissions(user_role):
    """Role के सभी permissions"""
    return role_permissions.get_user_permissions(user_role)

def has_all_permissions(user_role, perms):
    """सभी permissions हैं?"""
    return role_permissions.has_multiple_permissions(user_role, perms)

def has_any_permission(user_role, perms):
    """कोई भी permission है?"""
    return role_permissions.has_any_permission(user_role, perms)

def get_endpoints(user_role):
    """Accessible endpoints"""
    return role_permissions.get_accessible_endpoints(user_role)

def is_higher(role1, role2):
    """Role comparison"""
    return role_permissions.is_higher_role(role1, role2)