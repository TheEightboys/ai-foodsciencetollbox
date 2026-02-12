"""
Django Admin Site Customization
Customizes the admin interface for superadmin use
"""
from django.contrib import admin
from django.contrib.admin import AdminSite


def setup_admin_site():
    """Setup admin site customization - called from AppConfig.ready()"""
    # Customize admin site header and title
    admin.site.site_header = "Food Science Toolbox - Admin Panel"
    admin.site.site_title = "Food Science Toolbox Admin"
    admin.site.index_title = "Welcome to the Administration Panel"

# Customize admin site for better superadmin experience
class CustomAdminSite(AdminSite):
    site_header = "Food Science Toolbox - Admin Panel"
    site_title = "Food Science Toolbox Admin"
    index_title = "Welcome to the Administration Panel"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site, with better organization for superadmin.
        """
        app_dict = {}
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = self.has_module_permission(request)
            
            if has_module_perms:
                perms = self._get_perms_for_model(model, request)
                
                # Only show models that the user has permission to view
                if True:  # For superuser, show all
                    model_dict = {
                        'name': model._meta.verbose_name_plural,
                        'object_name': model._meta.object_name,
                        'perms': perms,
                        'admin_url': None,
                        'add_url': None,
                    }
                    
                    if perms.get('change') or perms.get('view'):
                        model_dict['view_only'] = not perms.get('change')
                        try:
                            model_dict['admin_url'] = self._get_admin_url_for_model(model, request)
                        except:
                            pass
                    
                    if perms.get('add'):
                        try:
                            model_dict['add_url'] = self._get_admin_url_for_model(model, request, 'add')
                        except:
                            pass
                    
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_label': app_label,
                            'app_url': self._get_admin_url_for_app(app_label, request),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }
        
        # Sort the apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list


class AdminConfig:
    """Admin configuration class for Django app config"""
    default_site = 'django.contrib.admin.sites.AdminSite'
