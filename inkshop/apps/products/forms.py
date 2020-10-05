import logging
from django.forms import ModelForm, CharField, TextInput
from products.models import Product, ProductPurchase, Purchase, Journey, ProductDay
from django.forms import modelformset_factory


class ProductDayForm(ModelForm):
    class Meta:
        model = ProductDay
        fields = [
            "product",
            "day_number",
            "template",
        ]


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "number_of_days",
            "slug",
            "has_epilogue",
        ]


class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "person",
            "total",
            "discount_code",
            "discount_amount",
        ]


class ProductPurchaseForm(ModelForm):
    class Meta:
        model = ProductPurchase
        fields = [
            "product",
            "purchase",
        ]


class JourneyForm(ModelForm):
    class Meta:
        model = Journey
        fields = [
            "productpurchase",
            "start_date",
        ]
