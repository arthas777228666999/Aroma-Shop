from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Min, Max
from account.models import Account
from .models import *
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView
from itertools import chain
from django.views.generic import FormView
from .models import Order, OrderItem

def home_screen_view(request):
    context = {
        'accounts': Account.objects.all(),
        'slides': CarouselSlide.objects.filter(is_active=True).order_by('order'),
        'text_messages': TextCarouselMessage.objects.filter(is_active=True),
    }
    return render(request, "shop/home.html", context)

def product_card_view(request, model_name, product_id):
    model_map = {
        'perfume': ProductPerfume,
        'candle': ProductCandle,
    }
    model = model_map.get(model_name)
    if not model:
        return redirect('home')  
    product = get_object_or_404(model, id=product_id)
    return render(request, 'shop/product_card.html', {
        'product': product,
        'model_name': model_name  
    })

def cart_view(request):
    cart_items = []
    total = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            total += item.product.price * item.quantity
    return render(request, "shop/cart.html", {'cart_items': cart_items, 'total': total})

def wishlist_view(request):
    wishlist_items = []
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, completed=False)
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
    return render(request, "shop/wishlist.html", {'wishlist_items': wishlist_items})

@login_required
def add_to_cart(request, model_name, product_id):
    model_map = {
        'perfume': ProductPerfume,
        'candle': ProductCandle,
    }
    model = model_map.get(model_name)
    if not model:
        return JsonResponse({'error': 'Некоректний товар'}, status=400)

    product = get_object_or_404(model, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user, completed=False)
    content_type = ContentType.objects.get_for_model(model)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        content_type=content_type,
        object_id=product.id,
    )
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_items_count': CartItem.objects.filter(cart=cart).count()
        })

    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

    return redirect('cart')

@login_required
def add_to_wishlist(request, model_name, product_id):
    model_map = {
        'perfume': ProductPerfume,
        'candle': ProductCandle,
    }
    model = model_map.get(model_name)
    if not model:
        return JsonResponse({'error': 'Некоректний товар'}, status=400)

    product = get_object_or_404(model, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user, completed=False)
    content_type = ContentType.objects.get_for_model(model)

    wishlist_item, created = WishlistItem.objects.get_or_create(
        content_type=content_type,
        object_id=product.id,
        wishlist=wishlist
    )

    if not created:
        wishlist_item.quantity += 1
    else:
        wishlist_item.quantity = 1

    wishlist_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'wishlist_items_count': WishlistItem.objects.filter(wishlist=wishlist).count()
        })

    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, item_id):
    try:
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
        wishlist_item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('wishlist')
    except Http404:
        messages.error(request, f"Товар #{item_id} не знайдено у вашому обраному.")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Товар не знайдено'}, status=404)
        return redirect('wishlist')

@require_POST
@login_required
def move_to_cart(request, item_id):
    try:
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
        product = wishlist_item.product  
        
        if not product:
            raise ValueError("Товар не знайдено")
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        content_type = wishlist_item.content_type
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            content_type=content_type,
            object_id=product.id,
        )
        
        if not created:
            cart_item.quantity += wishlist_item.quantity 
        else:
            cart_item.quantity = wishlist_item.quantity
            
        cart_item.save()
        wishlist_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Товар успішно переміщено до корзини'
            })
            
        messages.success(request, 'Товар успішно переміщено до корзини')
        return redirect('cart')
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in move_to_cart: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': f'Помилка: {str(e)}'
            }, status=500)
        messages.error(request, f"Помилка при переміщенні товару: {str(e)}")
        return redirect('wishlist')

def wishlist_toggle(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product_model = request.POST.get('model_name')  
        
        model_map = {
            'perfume': 'productperfume',
            'candle': 'productcandle',
            'productperfume': 'productperfume',
            'productcandle': 'productcandle',
        }
        
        model_name = model_map.get(product_model.lower())
        
        if not model_name:
            return JsonResponse({'error': 'Некоректний товар', 'received': product_model}, status=400)
            
        try:
            content_type = ContentType.objects.get(model=model_name)
            model_class = content_type.model_class()
            product = model_class.objects.get(id=product_id)
            
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            
            existing_item = WishlistItem.objects.filter(
                wishlist=wishlist,
                content_type=content_type,
                object_id=product.id
            ).first()
            
            if existing_item:
                existing_item.delete()
                return JsonResponse({'success': True, 'action': 'removed'})
            else:
                WishlistItem.objects.create(
                    wishlist=wishlist,
                    content_type=content_type,
                    object_id=product.id,
                    quantity=1
                )
                return JsonResponse({'success': True, 'action': 'added'})
                
        except ContentType.DoesNotExist:
            return JsonResponse({'error': 'Некоректний товар'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Помилка: {str(e)}'}, status=404)

    return JsonResponse({'error': 'Некоректний запит'}, status=400)

def product_list_view(request, product_class, template_name, product_type):
    products = product_class.objects.all()
    filter_form = ProductFilterForm(request.GET or None, product_class=product_class)
    
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        # Виправлення для фільтра наявності
        available = data.get('available')
        if available == 'True' or available == '1':
            products = products.filter(available=True)
        elif available == 'False' or available == '0':
            products = products.filter(available=False)
        
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        if min_price is not None and min_price != '':
            products = products.filter(price__gte=min_price)
        if max_price is not None and max_price != '':
            products = products.filter(price__lte=max_price)
            
        if hasattr(product_class, 'GENDER_CHOICES'):
            if data.get('gender'):
                products = products.filter(gender=data['gender'])
            if data.get('size'):
                products = products.filter(size=data['size'])
                
        if data.get('scent_group'):
            products = products.filter(scent_group=data['scent_group'])
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    for product in page_obj:
        product.model_name = product_class._meta.model_name
    
    price_range = product_class.objects.aggregate(min=Min('price'), max=Max('price'))
    
    context = {
        'form': filter_form,  # Додаємо також 'form' для сумісності з шаблоном
        'filter_form': filter_form,
        'products': page_obj,
        'product_count': products.count(),
        'price_range': price_range,
        'slide': ProductListPhoto.objects.filter(is_active=True).first(),
        'product_type': product_type,  # Додаємо тип продукту
    }
    
    return render(request, template_name, context)

def product_list_perf_view(request):
    return product_list_view(request, ProductPerfume, 'shop/product_list_perf.html', 'perfume')

def product_list_cand_view(request):
    return product_list_view(request, ProductCandle, 'shop/product_list_cand.html', 'candle')

def scent_of_month_view(request):
    scent_slide = ScentOfMonthPhoto.objects.filter(is_active=True).first()
    featured_products = ProductPerfume.objects.filter(is_scent_of_month=True, available=True)
    
    context = {
        'slide': scent_slide,
        'products': featured_products
    }
    
    return render(request, 'shop/scent_of_month.html', context)

def darkfem_collection_view(request):
    darkfem_slide = DarkfemCollectionPhoto.objects.filter(is_active=True).first()
    featured_products = ProductPerfume.objects.filter(is_darkfem_collection=True, available=True)
    
    context = {
        'slide': darkfem_slide,
        'products': featured_products
    }
    
    return render(request, 'shop/darkfem_collection.html', context)

def loveme_collection_view(request):
    loveme_slide = LovemeCollectionPhoto.objects.filter(is_active=True).first()
    featured_products = ProductPerfume.objects.filter(is_loveme_collection=True, available=True)
    
    context = {
        'slide': loveme_slide,
        'products': featured_products
    }
    
    return render(request, 'shop/loveme_collection.html', context)

def filtered_perfume_list_view(request, filter_type, filter_value):
    perfumes = ProductPerfume.objects.filter(available=True)
    title = "Аромати"

    if filter_type == "gender":
        perfumes = perfumes.filter(gender=filter_value)
        title = dict(ProductPerfume.GENDER_CHOICES).get(filter_value, title)
    elif filter_type == "scent":
        perfumes = perfumes.filter(scent_group=filter_value)
        title = dict(ProductPerfume.SCENT_GROUP_CHOICES).get(filter_value, title)
    elif filter_type == "size":
        perfumes = perfumes.filter(size=filter_value)
        title = f"Розмір: {filter_value} мл"
    elif filter_type == "bestseller":
        perfumes = perfumes.filter(is_bestseller=True)
        title = "Бестселери"
    elif filter_type == "featured":
        perfumes = perfumes.filter(is_featured=True)
        title = "Рекомендовані"

    title = title.upper()

    paginator = Paginator(perfumes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/perfume_filtered_list.html', {
        'products': page_obj,
        'title': title,
    })

def filtered_candle_list_view(request, filter_type, filter_value):
    candles = ProductCandle.objects.filter(available=True)
    title = "Аромати"

    if filter_type == "scent":
        candles = candles.filter(scent_group=filter_value)
        title = dict(ProductCandle.SCENT_GROUP_CHOICES).get(filter_value, title)
    elif filter_type == "bestseller":
        candles = candles.filter(is_bestseller=True)
        title = "Бестселери"
    elif filter_type == "featured":
        candles = candles.filter(is_featured=True)
        title = "Рекомендовані"

    title = title.upper()

    paginator = Paginator(candles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/candle_filtered_list.html', {
        'products': page_obj,
        'title': title,
    })

class SearchProductsView(ListView):
    """Класове представлення для пошуку товарів"""
    template_name = 'shop/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if query and len(query) >= 2:
            # Пошук парфумів
            perfumes = ProductPerfume.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(scent_group__icontains=query) |
                Q(top_notes__icontains=query) |
                Q(middle_notes__icontains=query) |
                Q(base_notes__icontains=query),
                available=True
            ).select_related()
            
            # Пошук свічок
            candles = ProductCandle.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query),
                available=True
            ).select_related()
            
            # Об'єднання результатів
            combined = list(chain(perfumes, candles))
            
            # Сортування за релевантністю (найбільш точні збіги спочатку)
            def relevance_score(product):
                score = 0
                query_lower = query.lower()
                name_lower = product.name.lower()
                
                if query_lower == name_lower:
                    score += 100
                elif name_lower.startswith(query_lower):
                    score += 50
                elif query_lower in name_lower:
                    score += 25
                
                if hasattr(product, 'brand') and product.brand and query_lower in product.brand.lower():
                    score += 10
                    
                return score
            
            combined.sort(key=relevance_score, reverse=True)
            return combined
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        context['results_count'] = len(self.get_queryset())
        
        # Додаткова інформація для шаблону
        if query:
            context['search_performed'] = True
        else:
            context['search_performed'] = False
            
        return context


def ajax_search_products(request):
    """AJAX представлення для живого пошуку"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        products = []
        
        if query and len(query) >= 2:
            # Пошук парфумів (без обмеження)
            perfumes = ProductPerfume.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(scent_group__icontains=query) |
                Q(top_notes__icontains=query) |
                Q(middle_notes__icontains=query) |
                Q(base_notes__icontains=query),
                available=True
            ).select_related()
            
            # Пошук свічок (без обмеження)
            candles = ProductCandle.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query),
                available=True
            ).select_related()
            
            # Формування результатів для парфумів
            for product in perfumes:
                try:
                    product_url = product.get_absolute_url() if hasattr(product, 'get_absolute_url') else reverse('perfume_detail', kwargs={'pk': product.pk})
                except:
                    product_url = f"/perfume/{product.pk}/"
                
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'description': (product.description[:80] + '...') if len(product.description) > 80 else product.description,
                    'price': str(product.price),
                    'image': product.picture.url if product.picture else '/static/images/no-image.jpg',
                    'url': product_url,
                    'type': 'perfume',
                    'brand': getattr(product, 'brand', ''),
                    'size': f"{product.size}мл" if hasattr(product, 'size') and product.size else ''
                })
            
            # Формування результатів для свічок
            for product in candles:
                try:
                    product_url = product.get_absolute_url() if hasattr(product, 'get_absolute_url') else reverse('candle_detail', kwargs={'pk': product.pk})
                except:
                    product_url = f"/candle/{product.pk}/"
                
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'description': (product.description[:80] + '...') if len(product.description) > 80 else product.description,
                    'price': str(product.price),
                    'image': product.picture.url if product.picture else '/static/images/no-image.jpg',
                    'url': product_url,
                    'type': 'candle',
                    'brand': getattr(product, 'brand', ''),
                })
            
            # Сортування за релевантністю
            def relevance_score(product):
                score = 0
                query_lower = query.lower()
                name_lower = product['name'].lower()
                
                if query_lower == name_lower:
                    score += 100
                elif name_lower.startswith(query_lower):
                    score += 80
                elif query_lower in name_lower:
                    score += 40
                
                if product['brand'] and query_lower in product['brand'].lower():
                    score += 10
                    
                return score
            
            products.sort(key=relevance_score, reverse=True)
            
            # Обмежуємо до 6 найрелевантніших
            products = products[:6]
            
        return JsonResponse({
            'products': products,
            'count': len(products),
            'query': query
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# Додаткова функція для автодоповнення пошуку
def search_suggestions(request):
    """Представлення для отримання підказок пошуку"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip().lower()
        suggestions = []
        
        if query and len(query) >= 1:
            # Отримання унікальних назв продуктів
            perfume_names = ProductPerfume.objects.filter(
                name__icontains=query, 
                available=True
            ).values_list('name', flat=True)

            candle_names = ProductCandle.objects.filter(
                name__icontains=query, 
                available=True
            ).values_list('name', flat=True)

            # Отримання унікальних брендів
            perfume_brands = ProductPerfume.objects.filter(
                brand__icontains=query, 
                available=True
            ).values_list('brand', flat=True).distinct()

            candle_brands = ProductCandle.objects.filter(
                brand__icontains=query, 
                available=True
            ).values_list('brand', flat=True).distinct()

            # Об'єднання
            all_suggestions = list(perfume_names) + list(candle_names) + list(perfume_brands) + list(candle_brands)
            
            # Унікальність і сортування за релевантністю
            unique = list(set(all_suggestions))

            def relevance_score(s):
                s_lower = s.lower()
                if s_lower == query:
                    return 100
                elif s_lower.startswith(query):
                    return 80
                elif query in s_lower:
                    return 40
                return 0

            unique.sort(key=relevance_score, reverse=True)
            suggestions = unique[:6]  # максимум 8
            
        return JsonResponse({
            'suggestions': suggestions,
            'query': query
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


class CheckoutView(FormView):
    template_name = 'shop/checkout.html'
    form_class = OrderForm
    success_url = '/thank-you/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user, completed=False).first()
            if cart:
                cart_items = CartItem.objects.filter(cart=cart)
                total = sum(item.product.price * item.quantity for item in cart_items)
                # item.product — працює тільки якщо у CartItem є generic relation
                for item in cart_items:
                    item.item_total = item.product.price * item.quantity
                context['cart_items'] = cart_items
                context['total'] = total
            else:
                context['cart_items'] = []
                context['total'] = 0
        return context

    def form_valid(self, form):
        order = form.save(commit=False)
        order.user = self.request.user if self.request.user.is_authenticated else None
        order.save()

        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user, completed=False).first()
            if cart:
                for item in CartItem.objects.filter(cart=cart):
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                cart.completed = True
                cart.save()
        return super().form_valid(form)

def about_us_view(request):
    return render(request, 'shop/about_us.html')

def partnership_view(request):
    return render(request, 'shop/partnership.html')

def delivery_info_view(request):
    return render(request, 'shop/delivery_info.html')

def contacts_view(request):
    return render(request, 'shop/contacts.html')        
