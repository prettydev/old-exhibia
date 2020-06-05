# -*- coding: utf-8 -*-
from exhibit.models import Exhibit
from django.db import models

class ExhibitWinnerPost(models.Model):
    image = models.ImageField(upload_to=u'winner_posts')
    exhibit = models.ForeignKey(Exhibit, unique=True)