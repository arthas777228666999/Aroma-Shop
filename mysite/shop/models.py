from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.conf import settings
import uuid

class AbstractProduct(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    price = models.IntegerField(verbose_name="Ціна")
    picture = models.ImageField(upload_to="products", blank=True, default="", verbose_name="Зображення")
    available = models.BooleanField(default=True, verbose_name="В наявності")
    description = models.TextField(blank=True, verbose_name="Опис")
    brand = models.CharField(max_length=100, blank=True, verbose_name="Бренд")
    top_notes = models.CharField(max_length=255, blank=True, verbose_name="Верхні ноти")
    middle_notes = models.CharField(max_length=255, blank=True, verbose_name="Ноти серця")
    base_notes = models.CharField(max_length=255, blank=True, verbose_name="Базові ноти")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендований товар")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_bestseller = models.BooleanField(default=False, verbose_name="Бестселер")

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])

    @property
    def get_display_price(self):
        return "{:,}".format(self.price).replace(',', ' ')

    @property
    def short_description(self):
        return self.description[:100] + '...' if self.description and len(self.description) > 100 else self.description or ""

    @property
    def discount_percentage(self):
        return int(100 - (self.price / self.old_price * 100)) if hasattr(self, 'old_price') and self.old_price and self.old_price > self.price else 0

class CarouselSlide(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to='carousel/', verbose_name="Зображення")
    button_text = models.CharField(max_length=50, default="Обрати", verbose_name="Текст кнопки")
    button_link = models.URLField(blank=True, verbose_name="Посилання кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = verbose_name_plural = "Карусель фото"

    def __str__(self):
        return self.title


class TextCarouselMessage(models.Model):
    text = models.CharField(max_length=200, verbose_name="Елемент текстової каруселі")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = "Елемент текстової каруселі"
        verbose_name_plural = "Карусель текст"

    def __str__(self):
        return self.text


class ProductPerfume(AbstractProduct):
    GENDER_CHOICES = [('male', 'Чоловічий'), ('female', 'Жіночий'), ('unisex', 'Унісекс')]
    SCENT_GROUP_CHOICES = [
        ('floral', 'Квіткові'),
        ('fresh and citrus', 'Свіжі та Цитрусові'),
        ('sweet and fruity', 'Солодкі та Фруктові'),
        ('oriental and spicy', 'Східні та Пряні'),
    ]
    SIZE_CHOICES = [('16', '16мл'), ('100', '100мл')]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Стать")
    scent_group = models.CharField(max_length=20, choices=SCENT_GROUP_CHOICES, blank=True, verbose_name="Група ароматів")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, verbose_name="Обʼєм")

    is_scent_of_month = models.BooleanField(default=False)
    is_darkfem_collection = models.BooleanField(default=False)
    is_loveme_collection = models.BooleanField(default=False)

    class Meta:
        verbose_name = verbose_name_plural = "Товари"

    def __str__(self):
        brand = f"{self.brand} " if self.brand else ""
        size = self.get_size_display() if self.size else ""
        return f"{brand}{self.name} ({size})"


class ProductCandle(AbstractProduct):
    SCENT_GROUP_CHOICES = [
        ('woody', 'Деревинні'),
        ('floral', 'Квіткові'),
        ('sweet and fruity', 'Солодкі та Фруктові'),
    ]
    scent_group = models.CharField(max_length=20, choices=SCENT_GROUP_CHOICES, blank=True, verbose_name="Група ароматів")

    class Meta:
        verbose_name = verbose_name_plural = "Товари"

    def __str__(self):
        return f"{self.brand} {self.name}" if self.brand else self.name

class ScentOfMonth(AbstractProduct):
    GENDER_CHOICES = [('female', 'Жіночий')]
    SCENT_GROUP_CHOICES = [
        ('floral', 'Квіткові'),
        ('sweet and fruity', 'Солодкі та Фруктові'),
    ]
    SIZE_CHOICES = [('100', '100мл')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name="Стать")
    scent_group = models.CharField(max_length=20, choices=SCENT_GROUP_CHOICES, blank=True, verbose_name="Група ароматів")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, verbose_name="Обʼєм")

    class Meta:
        verbose_name = verbose_name_plural = "Товари"

    def __str__(self):
        brand = f"{self.brand} " if self.brand else ""
        size = self.get_size_display() if self.size else ""
        return f"{brand}{self.name} ({size})"



class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitems')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    product = GenericForeignKey('content_type', 'object_id')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product}"

class Wishlist(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='wishlistitems')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    product = GenericForeignKey('content_type', 'object_id')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product}"

class BasePhoto(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to='slides/')
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class ProductListPhoto(BasePhoto):
    pass

class ScentOfMonthPhoto(BasePhoto):
    pass

class DarkfemCollectionPhoto(BasePhoto):
    pass

class LovemeCollectionPhoto(BasePhoto):
    pass

class Order(models.Model):
    country_region = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    np_branch = models.CharField(max_length=100)  # Відділення Нової Пошти
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Замовлення #{self.id} - {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default=1)