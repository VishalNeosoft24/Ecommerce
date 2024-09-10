from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def render_category_tree(context, categories):
    return render_to_string(
        "customer_portal/category_tree.html", {"categories": categories}
    )
