# -*- coding: utf-8 -*-
from account.classes import ReadOnlyAdmin
from django import forms
from django.contrib import admin
from .models import Item, Exhibit, ItemBrand, ItemCategory, ItemImage
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from social.apps.django_app.default.models import Association, Nonce, UserSocialAuth
from social.apps.django_app.default.admin import UserSocialAuthOption
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from mailqueue.models import MailerMessage
from mailqueue.admin import MailerAdmin


class ItemImagesInline(admin.TabularInline):
    model = ItemImage
    extra = 1


class AdminItem(ReadOnlyAdmin):
    list_display = ('name', 'price', 'amount', 'bidding_time', 'categories_inline', 
        'newbie', 'giveaway')

    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    inlines = [ItemImagesInline]

    def save_model(self, request, obj, form, change):
        super(AdminItem, self).save_model(request, obj, form, change)
        if not change:
            Exhibit.objects.create_from_item(obj)


class AdminItemCategory(ReadOnlyAdmin):
    prepopulated_fields = {"slug": ("name",)}


class AdminItemBrand(ReadOnlyAdmin):
    prepopulated_fields = {"slug": ("name",)}


class AdminExhibit(ReadOnlyAdmin):
    list_display = ('item', 'status', 'backers_count', 'last_bidder_name', 'ended_time', 
        'item_newbie', 'item_giveaway')
    list_filter = ('status', 'last_bidder_name',)
    search_fields = ('status', 'last_bidder_name', 'ended_unixtime', 'item__name')

    def item_newbie(self, obj):
        return obj.item.newbie

    item_newbie.short_description = 'Newbie Item'
    item_newbie.admin_order_field = 'item__newbie'
    item_newbie.boolean = True

    def item_giveaway(self, obj):
        return obj.item.giveaway

    item_giveaway.short_description = 'Giveaway Item'
    item_giveaway.admin_order_field = 'item__giveaway'
    item_giveaway.boolean = True



class ExtendFlatPageForm(FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage


class ExtendFlatPageAdmin(FlatPageAdmin, ReadOnlyAdmin):
    form = ExtendFlatPageForm


class ExtendGroupAdmin(GroupAdmin, ReadOnlyAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile',):
            pass
        else:
            return super(ExtendGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class ExtendUserSocialAuthAdmin(UserSocialAuthOption, ReadOnlyAdmin):

    def uid_observer_access(self, obj):
        return "XXXXX%s" % obj.uid[5:]
    
    uid_observer_access.short_description = 'uid'


class ExtendSiteAdmin(SiteAdmin, ReadOnlyAdmin):
    pass


class ExtendMailerAdmin(MailerAdmin, ReadOnlyAdmin):

     def get_model_perms(self, request):
        if not request.user.is_superuser and request.user.has_perm('account.readonly_profile'):
            return {
                'add': False,
                'change': False,
                'delete': False,
            }
        else:
            return super(ExtendMailerAdmin, self).get_model_perms(request)

# re-register some models to hide permissions from observer
admin.site.unregister(Group)
admin.site.register(Group, ExtendGroupAdmin)
admin.site.unregister([Nonce, Association, UserSocialAuth])
admin.site.register(UserSocialAuth, ExtendUserSocialAuthAdmin)
admin.site.unregister([Site, MailerMessage])
admin.site.register(Site, ExtendSiteAdmin)
admin.site.register(MailerMessage, ExtendMailerAdmin)

# re-register flatpage admin with ckeditor
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, ExtendFlatPageAdmin)

admin.site.register(Item, AdminItem)
admin.site.register(ItemCategory, AdminItemCategory)
admin.site.register(ItemBrand, AdminItemBrand)
admin.site.register(Exhibit, AdminExhibit)

