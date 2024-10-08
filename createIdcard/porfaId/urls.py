from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
app_name = 'porfa'

urlpatterns = [
        path('',views.generate_porfa_id_card, name='generate_porfa_id_card'),
        path('success/', views.modified_id_card, name='success'),
        path('download-pdf/<str:porfa_id>/', views.download_id_card_pdf, name='download_id_card_pdf'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
