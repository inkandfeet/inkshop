import logging
from django.forms import ModelForm, CharField, TextInput
from website.models import Template, Page, Post, Resource, Link
from django.forms import modelformset_factory


class TemplateForm(ModelForm):
    class Meta:
        model = Template
        fields = [
            "name",
            "nav",
            "content",
            "footer",
            "css",
            "js",
            "html_extra_classes",
            "body_override",
            "everything_override",
        ]


class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = [
            "name",
            "slug",
            "title",
            "description",
            "keywords",
            "template",
            "source_text",
            "rendered_html",
        ]


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            "name",
            "raw_markdown",
            "slug",
            "title",
            "description",
            "template",
            "publish_date",
            "published",
            "private",
            "context",
        ]


class ResourceForm(ModelForm):
    class Meta:
        model = Resource
        fields = [
            "name",
            "binary_file",
            "text_file",
            "mime_type",
            "hashed_filename",
            "content_size",
        ]


class LinkForm(ModelForm):
    class Meta:
        model = Link
        fields = [
            "name",
            "slug",
            "target_url",
            "title",
            "description",
            "publish_date",
            "published",
            "private",
            "thumbnail_image_source",
            "thumbnail_image",
            "destination_title",
            "destination_description",
        ]
