from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Lấy giá trị từ dictionary theo key"""
    return dictionary.get(key)

@register.filter
def concat(value, arg):
    """Concatenate strings"""
    return f"{value}_{arg}"