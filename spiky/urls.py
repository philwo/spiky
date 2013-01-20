# -*- coding: utf-8 -*-

# Spiky urls
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Starting page
    (r'^$', 'spiky.wiki.views.start'),

    # Account management
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'default/registration/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'default/registration/logged_out.html'}),
    (r'^accounts/signup/$', 'spiky.wiki.views.signup'),
    (r'^accounts/profile/$', 'spiky.wiki.views.profile'),
    (r'^accounts/password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'default/registration/password_change_form.html'}),
    (r'^accounts/password_change/done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'default/registration/password_change_done.html'}),
    (r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'default/registration/password_reset_form.html'}),
    (r'^accounts/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'default/registration/password_reset_done.html', 'email_template_name': 'default/registration/password_reset_email.html'}),

    # Dynamic pages
    (r'^search/$', 'spiky.wiki.views.search_pages'),
    (r'^list/$', 'spiky.wiki.views.list_pages'),
    (r'^calendar/$', 'spiky.wiki.views.view_calendar'),
    (r'^calendar/(?P<year>[^/]+)/(?P<month>[^/]+)/$', 'spiky.wiki.views.view_calendar'),
    (r'^tags/$', 'spiky.wiki.views.list_tags'),
    (r'^tags/(?P<tag_name>[^/]+)/$', 'spiky.wiki.views.view_tag'),

    # Static pages
    (r'^contact/$', 'spiky.wiki.views.contact'),
    (r'^imprint/$', 'spiky.wiki.views.imprint'),

    # Web services
    (r'^preview/$', 'spiky.wiki.views.preview'),
    (r'^compile/$', 'spiky.wiki.views.compile_all'),

    # Django admin
    #(r'^admin/', include('django.contrib.admin.urls')),

    # Normal Wiki pages
    (r'^uid/(?P<uid>[\d]+)/$', 'spiky.wiki.views.view_page_by_uid'),
    (r'^(?P<page_name>[^/]+)/log/$', 'spiky.wiki.views.show_log'),
    (r'^(?P<page_name>[^/]+)/save/$', 'spiky.wiki.views.save_page'),
    (r'^(?P<page_name>[^/]+)/edit/$', 'spiky.wiki.views.edit_page'),
    (r'^(?P<page_name>[^/]+)/delete/$', 'spiky.wiki.views.delete_page'),
    (r'^(?P<page_name>[^/]+)/(?P<rev>[\d]+)/restore/$', 'spiky.wiki.views.restore_page'),
    (r'^(?P<page_name>[^/]+)/(?P<rev>[\d]+)/$', 'spiky.wiki.views.view_page'),
    (r'^(?P<page_name>[^/]+)/$', 'spiky.wiki.views.view_page'),

    # Misc stuff
    (r'^merge/(?P<original>[\d]+)/(?P<theirs>[\d]+)/(?P<ours>[\d]+)/', 'spiky.wiki.views.merge'),
    (r'^diff/(?P<v1>[\d]+)/(?P<v2>[\d]+)/', 'spiky.wiki.views.diff'),
    (r'^compare/(?P<rev1>[\d]+)/(?P<rev2>[\d]+)/$', 'spiky.wiki.views.compare'),
)
