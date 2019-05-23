from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^rango/', include('rango.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
