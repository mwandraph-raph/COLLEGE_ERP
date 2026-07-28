from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Returns dictionary[key] inside templates.
    """
    if dictionary is None:
        return None

    return dictionary.get(key)


@register.filter
def has_group(user, group_name):
    """
    Usage:

    {% if user|has_group:"Exam Officer" %}
        ...
    {% endif %}
    """
    if user.is_anonymous:
        return False

    return user.groups.filter(name=group_name).exists()