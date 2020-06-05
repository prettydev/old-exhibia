# -*- coding: utf-8 -*-
from .models import ExhibitWinnerPost
from django.contrib import admin


class ExhibitWinnerPostAdmin(admin.ModelAdmin):
    pass

admin.site.register(ExhibitWinnerPost, ExhibitWinnerPostAdmin)