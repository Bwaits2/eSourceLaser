from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns, settings
from django.conf.urls import url
from . import views


urlpatterns = [

    # /
    url('^$', views.HomepageView.as_view(), name='homepage'),

    # /part/<id>/
    url(r'^part/(?P<pk>[0-9]+)/$', views.part_detail_view, name='part-detail'),

    # /part/<id>/edit/
    url(r'^part/(?P<pk>[0-9]+)/edit/$', views.edit_part_view, name='edit-part'),

    # /buyer/create_part/
    url(r'^buyer/create_part/$', views.CreatePartView.as_view(), name='create-part'),

    # /buyer/
    url(r'^buyer/$', views.buyer_home_view, name='buyer-home'),

    # /supplier/
    url(r'^supplier/$', views.supplier_home_view, name='supplier-home'),

    # /buyer/create_rfq/
    url(r'^buyer/create_rfq/$', views.CreateRFQView.as_view(), name="create-rfq"),

    # /rfq/<id>/
    url(r'^rfq/(?P<pk>[0-9]+)/$', views.rfq_detail_view, name='rfq-detail'),

    # /administration/
    url(r'^administration/$', views.admin_view, name='admin-page'),

    # /error/
    url(r'^error/$', views.error_view, name='error'),

    # /rfq/<id>/quote/
    url(r'^rfq/(?P<pk>[0-9]+)/quote/$', views.quote_rfq_view, name='quote-rfq'),

    # /rfq/<id>/pay/
    url(r'^rfq/(?P<pk>[0-9]+)/pay/$', views.buyer_payment_view, name='buyer-pay'),

    # /quote/<id>/
    url(r'^quote/(?P<pk>[0-9]+)/$', views.quote_detail_view, name='quote-detail'),

    # /shipment/<id>/
    url(r'^shipment/(?P<pk>[0-9]+)/$', views.shipment_view, name='shipment-detail'),

    # /home/
    url(r'^home/$', views.home, name='home'),

    # /faq/
    url(r'^faq/$', views.faq_view, name='faq'),

    # /supfaq/
    url(r'^supfaq/$', views.supplier_faq_view, name='supfaq'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

