"""OnlineApproval URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('PR/', include('PurchaseRequest.urls')),
    path('BS/', include('BonMerah.urls')),
    path('PO/', include('PurchaseOrder.urls')),
    path('SP/', include('SellingPrice.urls')),
    path('PP/', include('PurchasingPrice.urls')),
    path('CP/', include('CapitalExpenditure.urls')),
    path('BE/', include('Entertainment.urls')),
    path('Purchase/', include('PurchaseOnline.urls')),
    #path('LMK/', include('LMKSupplier.urls')),
    path('', views.home),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
