from django.contrib import admin
import json
import os
import uuid


class ReadOnlyAdmin(admin.ModelAdmin):
    """
    Extend ModelAdmin class for enabling "readonly permission. Be sure that readonly_profile permission is in database
    for module account and model profile "
    """
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile',):
            self.exclude = ('groups', 'user_permissions', 'categories', 'password',
                            'email', 'phone', 'address', 'to_address', 'uid',
                            'shipping_address', 'billing_address')

            return list(self.readonly_fields) + \
                [f.name for f in self.model._meta.fields if f.name not in (
                    'password', 'id', 'email', 'phone', 'address', 'to_address', 'uid',
                    'shipping_address', 'billing_address'
                )]
        else:
            return super(ReadOnlyAdmin, self).get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return False
        else:
            return super(ReadOnlyAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return False
        else:
            return super(ReadOnlyAdmin, self).has_delete_permission(request, obj)

    def get_prepopulated_fields(self, request, obj=None):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return {}
        else:
            return super(ReadOnlyAdmin, self).get_prepopulated_fields(request, obj)

    def get_actions(self, request):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return {}
        else:
            return super(ReadOnlyAdmin, self).get_actions(request)

    def get_inline_instances(self, request, obj=None):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return []
        else:
            return super(ReadOnlyAdmin, self).get_inline_instances(request, obj)

    def get_list_display(self, request):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            fields = [field if field not in ['email', 'phone', 'uid', 'to_address']
                      else '%s_observer_access' % field if field == 'uid' else '' for field in list(self.list_display)]
            return filter(lambda x: x != '', fields)
        else:
            return super(ReadOnlyAdmin, self).get_list_display(request)


class ImageUploader(object):

    def __init__(self, allowed_extensions=None, sizelimit=None):
        self.allowed_extensions = allowed_extensions or []
        self.sizelimit = sizelimit or 20971520

    def handle_upload(self, request, upload_directory):
        uploaded = request.read
        filesize = int(uploaded.im_self.META["CONTENT_LENGTH"])
        filename = request.POST['qqfilename']

        if self._get_extension_from_file_name(filename) in self.allowed_extensions or ".*" in self.allowed_extensions:
            if filesize <= self.sizelimit:
                unique_filename = generate_unique_filename(filename)
                path = os.path.join(upload_directory, unique_filename)
                with open(path, 'wb+') as destination:
                    for chunk in request.FILES["qqfile"].chunks():
                        destination.write(chunk)
                return json.dumps({"success": True, 'uploadName': unique_filename})
            else:
                return json.dumps({"error": "File is too large."})
        else:
            return json.dumps({"error": "File has an invalid extension."})

    def _get_extension_from_file_name(self, file_name):
        filename, extension = os.path.splitext(file_name)
        return extension.lower()


def generate_unique_filename(filename):
    extension = filename.split(".")[-1]
    unique_filename = str(uuid.uuid4())
    return "%s.%s" % (unique_filename, extension)
