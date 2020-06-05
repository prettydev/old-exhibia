# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table(u'account_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('bids', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('bonus_bids', self.gf('django.db.models.fields.PositiveIntegerField')(default=3)),
            ('funding_credits', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('referer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.Profile'], null=True, blank=True)),
            ('referer_activated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('win_limited_x2', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_banned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('points', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('wins_number', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_win_unixtime', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('last_win_unixtime_additional', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('is_email_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_phone_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('facebook_img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('google_img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'account', ['Profile'])

        # Adding M2M table for field groups on 'Profile'
        m2m_table_name = db.shorten_name(u'account_profile_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'account.profile'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'Profile'
        m2m_table_name = db.shorten_name(u'account_profile_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'account.profile'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'permission_id'])

        # Adding model 'Address'
        db.create_table(u'account_address', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addresses', to=orm['account.Profile'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'account', ['Address'])

        # Adding model 'ProfileItemNotification'
        db.create_table(u'account_profileitemnotification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wishlist', to=orm['account.Profile'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', to=orm['exhibit.Item'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'account', ['ProfileItemNotification'])

        # Adding model 'IpAddress'
        db.create_table(u'account_ipaddress', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ip_addresses', to=orm['account.Profile'])),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('last_login', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'account', ['IpAddress'])

        # Adding unique constraint on 'IpAddress', fields ['user', 'ip_address']
        db.create_unique(u'account_ipaddress', ['user_id', 'ip_address'])

        # Adding model 'VerificationProfile'
        db.create_table(u'account_verificationprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.Profile'])),
            ('verification_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('attempts', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'account', ['VerificationProfile'])

        # Adding unique constraint on 'VerificationProfile', fields ['user', 'type']
        db.create_unique(u'account_verificationprofile', ['user_id', 'type'])

        # Adding model 'SmsMessage'
        db.create_table(u'account_smsmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('error_message', self.gf('django.db.models.fields.TextField')(max_length=500, null=True, blank=True)),
            ('verification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.VerificationProfile'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'account', ['SmsMessage'])

        # Adding model 'Coupon'
        db.create_table(u'account_coupon', (
            ('code', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True, primary_key=True, db_index=True)),
            ('expired_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expired_after_uses', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('bonus_bids_amount', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('bonus_bids_percent', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('min_package_amount', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('funding_percent', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'account', ['Coupon'])


    def backwards(self, orm):
        # Removing unique constraint on 'VerificationProfile', fields ['user', 'type']
        db.delete_unique(u'account_verificationprofile', ['user_id', 'type'])

        # Removing unique constraint on 'IpAddress', fields ['user', 'ip_address']
        db.delete_unique(u'account_ipaddress', ['user_id', 'ip_address'])

        # Deleting model 'Profile'
        db.delete_table(u'account_profile')

        # Removing M2M table for field groups on 'Profile'
        db.delete_table(db.shorten_name(u'account_profile_groups'))

        # Removing M2M table for field user_permissions on 'Profile'
        db.delete_table(db.shorten_name(u'account_profile_user_permissions'))

        # Deleting model 'Address'
        db.delete_table(u'account_address')

        # Deleting model 'ProfileItemNotification'
        db.delete_table(u'account_profileitemnotification')

        # Deleting model 'IpAddress'
        db.delete_table(u'account_ipaddress')

        # Deleting model 'VerificationProfile'
        db.delete_table(u'account_verificationprofile')

        # Deleting model 'SmsMessage'
        db.delete_table(u'account_smsmessage')

        # Deleting model 'Coupon'
        db.delete_table(u'account_coupon')


    models = {
        u'account.address': {
            'Meta': {'object_name': 'Address'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': u"orm['account.Profile']"})
        },
        u'account.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'bonus_bids_amount': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bonus_bids_percent': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'primary_key': 'True', 'db_index': 'True'}),
            'expired_after_uses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expired_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'funding_percent': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'min_package_amount': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'account.ipaddress': {
            'Meta': {'ordering': "('-last_login',)", 'unique_together': "(('user', 'ip_address'),)", 'object_name': 'IpAddress'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_login': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ip_addresses'", 'to': u"orm['account.Profile']"})
        },
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
        u'account.profileitemnotification': {
            'Meta': {'object_name': 'ProfileItemNotification'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': u"orm['exhibit.Item']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wishlist'", 'to': u"orm['account.Profile']"})
        },
        u'account.smsmessage': {
            'Meta': {'object_name': 'SmsMessage'},
            'error_message': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'verification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.VerificationProfile']", 'null': 'True', 'blank': 'True'})
        },
        u'account.verificationprofile': {
            'Meta': {'unique_together': "(('user', 'type'),)", 'object_name': 'VerificationProfile'},
            'attempts': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.Profile']"}),
            'verification_key': ('django.db.models.fields.CharField', [], {'max_length': '40'})
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
        }
    }

    complete_apps = ['account']