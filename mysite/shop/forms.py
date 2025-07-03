from django import forms
from .models import ProductPerfume, ProductCandle

class ProductFilterForm(forms.Form):
    AVAILABLE_CHOICES = [
        ('1', 'В наявності'),
        ('0', 'Немає на складі'),
    ]

    available = forms.ChoiceField(
        required=False,
        choices=[('', 'Усі')] + AVAILABLE_CHOICES,
        widget=forms.Select(),
        label="Наявність"
    )

    min_price = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'placeholder': 'від'}),
        label="Ціна від"
    )

    max_price = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'placeholder': 'до'}),
        label="Ціна до"
    )

    def __init__(self, *args, product_class=None, **kwargs):
        super().__init__(*args, **kwargs)

        if product_class == ProductPerfume:
            self.fields['gender'] = forms.ChoiceField(
                required=False,
                choices=[('', 'Усі')] + list(ProductPerfume.GENDER_CHOICES),
                label="Стать"
            )
            self.fields['scent_group'] = forms.ChoiceField(
                required=False,
                choices=[('', 'Усі')] + list(ProductPerfume.SCENT_GROUP_CHOICES),
                label="Група ароматів"
            )
            self.fields['size'] = forms.ChoiceField(
                required=False,
                choices=[('', 'Усі')] + list(ProductPerfume.SIZE_CHOICES),
                label="Обʼєм"
            )
        elif product_class == ProductCandle:
            self.fields['scent_group'] = forms.ChoiceField(
                required=False,
                choices=[('', 'Усі')] + list(ProductCandle.SCENT_GROUP_CHOICES),
                label="Група ароматів"
            )

        # Apply CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-select' if isinstance(self.fields[field].widget, forms.Select) else 'form-control'
            })


class OrderForm(forms.Form):
    country_region = forms.CharField(label="Країна/Регіон", max_length=100)
    first_name = forms.CharField(label="Ім'я", max_length=50)
    last_name = forms.CharField(label="Прізвище", max_length=50)
    np_branch = forms.CharField(label="Відділення Нової Пошти", max_length=100)
    city = forms.CharField(label="Місто", max_length=100)
    phone = forms.CharField(label="Телефон", max_length=20)