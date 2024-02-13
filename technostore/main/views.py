from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.models import TechnoAdmin
from main.models import NewCategory
from main.models import Tag
from main.models import Color
from django.contrib.auth.hashers import make_password,check_password
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from main.models import Product
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from random import sample
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


import paypalrestsdk
from django.shortcuts import render, redirect
from django.conf import settings

paypalrestsdk.configure({
    "mode": "sandbox",  
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})





def sepet(request):
    products_in_cart = request.session.get('sepet', [])
    total_price = sum(float(product['sale_price']) for product in products_in_cart)

    return render(request, 'main/shop-cart.html', {'products_in_cart': products_in_cart, 'total_price': total_price})







def sepete_ekle(request, product_id):
    product = Product.objects.get(id=product_id)
    products_in_cart = request.session.get('sepet', [])
    products_in_cart.append({'id': product.id, 'title': product.title, 'primary_photo_url': product.primary_photo.url, 'sale_price': str(product.sale_price)})

    request.session['sepet'] = products_in_cart
    return redirect('home')






def sepetten_cikar(request, product_id):
    products_in_cart = request.session.get('sepet', [])
    for index, product in enumerate(products_in_cart):
        if product['id'] == product_id:
            del products_in_cart[index]
            break
    request.session['sepet'] = products_in_cart
    return redirect('sepet')








def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    return render(request, 'main/single-product.html', {'product': product})







def home(request):

    products   = Product.objects.all().order_by('-id')[:12]

    all_products = list(Product.objects.all())
    random_products = sample(all_products, min(len(all_products), 12)) 
    categories = NewCategory.objects.filter(parent=None)[:5]
    return render(request, 'main/home.html', {'products': products,'random_products': random_products, 'categories': categories})






def shop(request, category_slug):
    category = get_object_or_404(NewCategory, slug=category_slug)
    products = Product.objects.filter(Q(parent_category=category) | Q(sub_category=category) | Q(sub_sub_category=category))
    
 
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 6) 

    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        
        page_products = paginator.page(1)
    except EmptyPage:
        
        page_products = paginator.page(paginator.num_pages)

    return render(request, 'main/shop.html', {'products': page_products})








def get_categories(request, category_slug):
    if category_slug == 'all-categories':
        all_categories = NewCategory.objects.all()
        categories_html = render_to_string('main/categories.html', {'categories': all_categories})
    else:
        category = NewCategory.objects.get(slug=category_slug)
        categories_html = render_to_string('main/categories.html', {'category': category})

    return JsonResponse({'categories_html': categories_html})







def fetch_products(request):
    category_slug = request.GET.get('category_slug')

    if category_slug:
        selected_category = get_object_or_404(NewCategory, slug=category_slug)
        filter_products = Product.objects.filter(parent_category=selected_category)[:8]
    else:

        filter_products = Product.objects.all()

    product_html = render_to_string('main/prj.html', {'filter_products': filter_products})
    return JsonResponse({'product_html': product_html})











def search(request):    
    search_query = request.GET.get('search', '')
    search_products = Product.objects.filter(
        Q(title__icontains=search_query) |
        Q(parent_category__title__icontains=search_query) |
        Q(sub_category__title__icontains=search_query) |
        Q(sub_sub_category__title__icontains=search_query)
    ).distinct()

    paginator = Paginator(search_products, 12)  

    page_number = request.GET.get('page')
    try:
        search_products = paginator.page(page_number)
    except PageNotAnInteger:
        search_products = paginator.page(1)
    except EmptyPage:
        search_products = paginator.page(paginator.num_pages)

    return render(request, 'main/search.html', {'search_products': search_products, 'search_query': search_query})







def contact(request):
    return render(request,'main/contact.html')










def addproduct(request):
    categories = NewCategory.objects.all()
    return render(request, 'dashboard/dashboard-add-product.html', {'categories': categories})





def add_category(request):
    if request.method == 'POST':
        category_title = request.POST.get('title')
        category_keywords = request.POST.get('categoryType')
        category_description = request.POST.get('categoryType')  
        category_icon = request.POST.get('icon')
        category_slug = request.POST.get('slug')

        parent_id = request.POST.get('parent')  

        if parent_id:
            parent_category = NewCategory.objects.get(pk=parent_id)
        else:
            parent_category = None

        new_category = NewCategory.objects.create(
            title=category_title,
            category_keywords=category_keywords,
            category_description=category_description,
            icon=category_icon,
            slug=category_slug,
            parent=parent_category
        )

        return redirect('add_category')

    categories = NewCategory.objects.all()
    return render(request, 'dashboard/dashboard-category.html', {'categories': categories})






def category(request):
    categories = NewCategory.objects.all()
    return render(request, 'dashboard/dashboard-category.html', {'categories': categories})






def delete_selected_categories(request):
    if 'selected_categories' in request.POST:
        selected_category_ids = request.POST.getlist('selected_categories')
        NewCategory.objects.filter(id__in=selected_category_ids).delete()
    return redirect('category')




def get_sub_categories(request, parent_id):  
    parent_category = NewCategory.objects.get(pk=parent_id)
    sub_categories = parent_category.get_children()
    data = {'sub_categories': [{'id': sub_category.id, 'title': sub_category.title} for sub_category in sub_categories]}
    return JsonResponse(data)


def get_sub_sub_categories(request, sub_category_id):  
    sub_category = NewCategory.objects.get(pk=sub_category_id)
    sub_sub_categories = sub_category.get_children()
    data = {'sub_sub_categories': [{'id': sub_sub_category.id, 'title': sub_sub_category.title} for sub_sub_category in sub_sub_categories]}
    return JsonResponse(data)





# Admin manager Class  and functions
class TechnoAdminManager:
    @staticmethod
    def add_techno_admin(request):   
        username = 'gulsare'
        password = 'gulsare1234'
        email = 'gulu@gmail.com'  

        hashed_password = make_password(password)
        TechnoAdmin.objects.create(username=username, password=hashed_password, email=email)
        return HttpResponse("TechnoAdmin eklendi!")

        # Product.objects.all().delete()
        # return HttpResponse("TechnoAdmin silindi")




    @staticmethod
    def login(request):
        error_message = None

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            try:
                techno_admin = TechnoAdmin.objects.get(username=username)

                if check_password(password, techno_admin.password):
                    request.session['is_logged_in'] = True
                    return redirect('login')
                else:
                    error_message = "Invalid Username/Password"
            except ObjectDoesNotExist:
                error_message = "Invalid Username/Password"
        return render(request, "dashboard/admin.html", {'error_message': error_message})





    @staticmethod
    def adminlogout(request):
        request.session['is_logged_in'] = False
        logout(request)
        return redirect('home')




def add_product(request):
    if request.method == 'POST':

        title = request.POST.get('title')
        brand = request.POST.get('brand')
        slug = slugify(title)
        product_count = request.POST.get('product_count')
        sku = request.POST.get('sku')
        stock_status = request.POST.get('stock_status')
        regular_price = request.POST.get('regular_price')
        sale_price = request.POST.get('sale_price')
        
        parent_category_id = request.POST.get('parent_category')
        sub_category_id = request.POST.get('sub_category')
        sub_sub_category_id = request.POST.get('sub_sub_category')
        
        parent_category_obj = NewCategory.objects.get(id=parent_category_id)
        sub_category_obj = NewCategory.objects.get(id=sub_category_id)
        sub_sub_category_obj = NewCategory.objects.get(id=sub_sub_category_id)

        description = request.POST.get('description')
        primary_photo = request.FILES.get('primary_photo')
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')
        photo4 = request.FILES.get('photo4')


        product_tags = request.POST.get('product_tags', '')
        tags_list = product_tags.split('|')
        print(tags_list)

        product_color = request.POST.get('product_colors', '')
        color_list = product_color.split('|')
        print(color_list)


        product = Product.objects.create(
            title=title,
            brand=brand,
            slug=slug,
            product_count=product_count,
            sku=sku,
            stock_status=stock_status,
            regular_price=regular_price,
            sale_price=sale_price,
            
            parent_category=parent_category_obj,
            sub_category=sub_category_obj,
            sub_sub_category=sub_sub_category_obj,

            description=description,
            primary_photo=primary_photo,
            photo1=photo1,
            photo2=photo2,
            photo3=photo3,
            photo4=photo4
        )

        for tag in tags_list:
            product.tags.create(tag=tag)

        for color in color_list:
            product.colors.create(color=color)


        messages.success(request, 'Product added successfully.')


        return redirect('addproduct') 

    else:

        categories = NewCategory.objects.all()
        return render(request, 'dashboard/dashboard-add-product.html', {'categories': categories}) 
    
