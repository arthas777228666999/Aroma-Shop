from django import template

register = template.Library()

@register.filter
def split_paragraph(value, max_len=48):
    if not isinstance(value, str):
        return value
    if len(value) <= max_len:
        return value
    split_pos = value.rfind(' ', 0, max_len)
    if split_pos == -1:
        split_pos = max_len
    return value[:split_pos] + '<br>' + value[split_pos+1:]