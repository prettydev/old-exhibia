# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # dirty hack to execute migration
        return
        
        # Adding model 'ItemBrand'
        db.create_table(u'exhibit_itembrand', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=250)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'exhibit', ['ItemBrand'])

        # Adding model 'ItemCategory'
        db.create_table(u'exhibit_itemcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=250)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'exhibit', ['ItemCategory'])

        # Adding model 'Item'
        db.create_table(u'exhibit_item', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
            ('our_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('amount', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('brand', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exhibit.ItemBrand'])),
            ('bidding_time', self.gf('django.db.models.fields.SmallIntegerField')(default=600)),
            ('description', self.gf('tinymce.models.HTMLField')(default='', blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('giveaway', self.gf('django.db.models.fields.BooleanField')()),
            ('funding_credits', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('standard_shipping_price', self.gf('django.db.models.fields.SmallIntegerField')(default=7, null=True, blank=True)),
            ('priority_shipping_price', self.gf('django.db.models.fields.SmallIntegerField')(default=15, null=True, blank=True)),
            ('lock_after', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('newbie', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'exhibit', ['Item'])

        # Adding M2M table for field categories on 'Item'
        m2m_table_name = db.shorten_name(u'exhibit_item_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('item', models.ForeignKey(orm[u'exhibit.item'], null=False)),
            ('itemcategory', models.ForeignKey(orm[u'exhibit.itemcategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['item_id', 'itemcategory_id'])

        # Adding model 'ItemImage'
        db.create_table(u'exhibit_itemimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['exhibit.Item'])),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'exhibit', ['ItemImage'])

        # Adding model 'Exhibit'
        db.create_table(u'exhibit_exhibit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='exhibits', to=orm['exhibit.Item'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='funding', max_length=15, db_index=True)),
            ('amount_funded', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('new_bidding_time', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('last_bidder_name', self.gf('django.db.models.fields.CharField')(default='', max_length=50, db_index=True, blank=True)),
            ('backers_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_bidder_member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.Profile'], null=True, blank=True)),
            ('started_unixtime', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('last_bidder_before_reset', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reseted_exhibits', null=True, to=orm['account.Profile'])),
            ('ended_unixtime', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('paused_unixtime', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('funded_unixtime', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('in_queue', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'exhibit', ['Exhibit'])

        # Adding model 'Bid'
        db.create_table(u'exhibit_bid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exhibit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bids', to=orm['exhibit.Exhibit'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.Profile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'exhibit', ['Bid'])

        # Adding model 'Fund'
        db.create_table(u'exhibit_fund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exhibit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exhibit.Exhibit'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.Profile'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal(u'exhibit', ['Fund'])


    def backwards(self, orm):
        # Deleting model 'ItemBrand'
        db.delete_table(u'exhibit_itembrand')

        # Deleting model 'ItemCategory'
        db.delete_table(u'exhibit_itemcategory')

        # Deleting model 'Item'
        db.delete_table(u'exhibit_item')

        # Removing M2M table for field categories on 'Item'
        db.delete_table(db.shorten_name(u'exhibit_item_categories'))

        # Deleting model 'ItemImage'
        db.delete_table(u'exhibit_itemimage')

        # Deleting model 'Exhibit'
        db.delete_table(u'exhibit_exhibit')

        # Deleting model 'Bid'
        db.delete_table(u'exhibit_bid')

        # Deleting model 'Fund'
        db.delete_table(u'exhibit_fund')


    models = {
        u'account.profile': {
            'Meta': {'object_name': 'Profile'},
            'bids': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'bonus_bids': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'facebook_img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'funding_credits': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'google_img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_banned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_email_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_phone_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'last_payment_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_win_unixtime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'last_win_unixtime_additional': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'referer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.Profile']", 'null': 'True', 'blank': 'True'}),
            'referer_activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'win_limited_x2': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wins_number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'exhibit.bid': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Bid'},
            'exhibit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bids'", 'to': u"orm['exhibit.Exhibit']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.Profile']"})
        },
        u'exhibit.exhibit': {
            'Meta': {'object_name': 'Exhibit'},
            'amount_funded': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'backers_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ended_unixtime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'funded_unixtime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_queue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exhibits'", 'to': u"orm['exhibit.Item']"}),
            'last_bidder_before_reset': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reseted_exhibits'", 'null': 'True', 'to': u"orm['account.Profile']"}),
            'last_bidder_member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.Profile']", 'null': 'True', 'blank': 'True'}),
            'last_bidder_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'new_bidding_time': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'paused_unixtime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'started_unixtime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'funding'", 'max_length': '15', 'db_index': 'True'})
        },
        u'exhibit.fund': {
            'Meta': {'object_name': 'Fund'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'exhibit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exhibit.Exhibit']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.Profile']"})
        },
        u'exhibit.item': {
            'Meta': {'object_name': 'Item'},
            'amount': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bidding_time': ('django.db.models.fields.SmallIntegerField', [], {'default': '600'}),
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exhibit.ItemBrand']"}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['exhibit.ItemCategory']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'funding_credits': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'giveaway': ('django.db.models.fields.BooleanField', [], {}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'lock_after': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'newbie': ('django.db.models.fields.BooleanField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'our_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'priority_shipping_price': ('django.db.models.fields.SmallIntegerField', [], {'default': '15', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'standard_shipping_price': ('django.db.models.fields.SmallIntegerField', [], {'default': '7', 'null': 'True', 'blank': 'True'})
        },
        u'exhibit.itembrand': {
            'Meta': {'object_name': 'ItemBrand'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'exhibit.itemcategory': {
            'Meta': {'object_name': 'ItemCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'exhibit.itemimage': {
            'Meta': {'object_name': 'ItemImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['exhibit.Item']"})
        }
    }

    complete_apps = ['exhibit']