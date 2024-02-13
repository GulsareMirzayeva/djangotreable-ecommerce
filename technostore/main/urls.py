from django.urls import path
from .import views




urlpatterns = [
    path('',views.home,name='home'),
    path('search',views.search,name='search'),
    path('contact',views.contact,name='contact'),
    path('addproduct',views.addproduct,name='addproduct'),
    path('add_product',views.add_product,name='add_product'),
    path('techno', views.TechnoAdminManager.login,name="login"), 
    path('category', views.category,name="category"), 
    path('adminlogout', views.TechnoAdminManager.adminlogout, name='adminlogout'),
    path('add_category', views.add_category, name='add_category'),
    path('get-categories/<str:category_slug>/', views.get_categories, name='get_categories'),
    path('get_sub_categories/<int:parent_id>/', views.get_sub_categories, name='get_sub_categories'),
    path('get_sub_sub_categories/<int:sub_category_id>/', views.get_sub_sub_categories, name='get_sub_sub_categories'),
    path('delete_selected_categories', views.delete_selected_categories, name='delete_selected_categories'),
    path('fetch-products/', views.fetch_products, name='fetch_products'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('shop/<slug:category_slug>/', views.shop, name='shop'),
    path('sepet/', views.sepet, name='sepet'),
    path('sepete-ekle/<int:product_id>/', views.sepete_ekle, name='sepete_ekle'),
    path('sepetten-cikar/<int:product_id>/', views.sepetten_cikar, name='sepetten_cikar'),

    # path('add_techno_admin/', views.TechnoAdminManager.add_techno_admin, name='add_techno_admin'), # Sayta admin elave etmek ucun url views.py add_techno_admin function
]