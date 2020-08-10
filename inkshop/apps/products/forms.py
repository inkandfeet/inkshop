import logging
from django.forms import ModelForm, CharField, TextInput
from products.models import Product, ProductPurchase, Purchase, Journey
from django.forms import modelformset_factory


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
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
            "product",
            "productpurchase",
            "start_date",
        ]
