from django.core.cache import cache

from .models import Category


def build_category_tree(categories):
    category_map = {cat['id']: cat for cat in categories}
    tree = []

    for cat in categories:
        cat['children'] = []

    for cat in categories:
        parent_id = cat['sub_category_id']
        if parent_id:
            parent = category_map.get(parent_id)
            if parent:
                parent['children'].append(cat)
        else:
            tree.append(cat)

    return tree


def global_categories(request):
    category_tree = cache.get('categories')
    if not category_tree:
        categories = Category.objects.all().order_by('title').values('id', 'title', 'slug', 'sub_category_id')
        category_tree = build_category_tree(list(categories))
        cache.set('categories', category_tree, 300 * 60)

    return {
        'categories': category_tree
    }
