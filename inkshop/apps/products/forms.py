import logging
from django.forms import ModelForm, CharField, TextInput
from products.models import Product, ProductPurchase, Purchase, Journey, ProductDay
from products.models import BestimatorExperiment, BestimatorExperimentChoice
from django.forms import modelformset_factory


class ProductDayForm(ModelForm):
    class Meta:
        model = ProductDay
        fields = [
            "product",
            "day_number",
            # "template",
            "pre_day_message",
        ]


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "number_of_days",
            "slug",
            "has_epilogue",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_beta_price_id",
            "journey_singular_name",
            "journey_plural_name",
            "purchase_message",
            "is_course",
            "is_downloadable",
        ]


class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "person",
            "total",
            "discount_code",
            "discount_amount",
            "refunded",
            "refund_feedback",
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


class BestimatorExperimentForm(ModelForm):
    class Meta:
        model = BestimatorExperiment
        fields = [
            "name",
            "slug",
        ]


class BestimatorExperimentChoiceForm(ModelForm):
    class Meta:
        model = BestimatorExperimentChoice
        fields = [
            "experiment",
            "name",
            "slug",
            "pattern",
            "url",
            "template_name",
        ]
