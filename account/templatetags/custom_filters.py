from django import template

register = template.Library()


@register.filter
def percent_of(value, total):
    try:
        value = float(value)
        total = float(total)
        return round((value / total) * 100, 2)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.filter
def get_promotion_progress(current_stat, rank):
    max_val = 3000000 if rank == 'bronze' else 9000000
    progress = (current_stat.monthly_sells / max_val) * 100
    return min(round(progress), 100)
