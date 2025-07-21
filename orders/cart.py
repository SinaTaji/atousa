from products.models import ProductVariant

Cart_Session_Id = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(Cart_Session_Id, {})
        self.session[Cart_Session_Id] = self.cart
        self._variants = None  # کش برای جلوگیری از کوئری تکراری

    def _get_variants(self):
        if self._variants is None:
            variant_ids = self.cart.keys()
            self._variants = {
                str(v.id): v for v in ProductVariant.objects.filter(id__in=variant_ids)
                .select_related('product', 'color', 'size')
            }
        return self._variants

    def __iter__(self):
        variants = self._get_variants()
        for key, item in self.cart.items():
            variant = variants.get(key)
            if not variant:
                continue

            yield {
                **item,
                'variant_id': variant.id,
                'variant_stock': variant.stock,
                'product_title': variant.product.title,
                'product_url': variant.product.get_absolute_url(),
                'product_model': variant.product.model,
                'product_code': variant.product.code,
                'color_name': variant.color.title if variant.color else "",
                'size_name': variant.size.title if variant.size else "",
                'price': variant.price,
                'variant_image_url': variant.image.url if variant.image else "",
                'has_discount': variant.has_discount,
                'get_discounted_price': variant.get_discounted_price(),
                'discount': variant.discount,
                'item_discount': variant.how_mutch_discounted(),
                'total_discount': variant.how_mutch_discounted() * int(item['quantity']),
                'total_price': variant.get_discounted_price() * int(item['quantity']),
            }

    def __len__(self):
        return sum(int(item['quantity']) for item in self.cart.values())

    def increase_quantity(self, key):
        if key in self.cart:
            self.cart[key]['quantity'] += 1
            self.save()

    def decrease_quantity(self, key):
        if key in self.cart:
            if self.cart[key]['quantity'] > 1:
                self.cart[key]['quantity'] -= 1
            else:
                del self.cart[key]
            self.save()

    def add(self, variant, quantity):
        product_id = str(variant.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}
        self.cart[product_id]['quantity'] += quantity
        self._variants = None  # invalidate cache
        self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self._variants = None
            self.save()

    def total(self):
        variants = self._get_variants()
        return sum(
            variants[key].get_discounted_price() * int(item['quantity'])
            for key, item in self.cart.items() if key in variants
        )

    def get_total_price(self):
        total = self.total()
        gift = self.session.get('gift')
        if gift:
            percent = gift.get('percent', 0)
            total -= round(total * (percent / 100))
        return total

    def get_total_org_price(self):
        variants = self._get_variants()
        return sum(
            variants[key].price * int(item['quantity'])
            for key, item in self.cart.items() if key in variants
        )

    def get_total_discount(self):
        variants = self._get_variants()
        total = sum(
            variants[key].how_mutch_discounted() * int(item['quantity'])
            for key, item in self.cart.items() if key in variants
        )
        gift = self.session.get('gift')
        if gift:
            price = self.total()
            percent = gift.get('percent', 0)
            total += price * (percent / 100)
        return total

    def send_free(self):
        if self.session.get('shipping_method', 'pishteaz') == 'tipax':
            return ''
        remaining = 2_000_000 - self.get_total_price()
        return max(0, remaining)

    def get_price_post(self):
        return self.get_total_price() + 69000

    def save(self):
        self.session.modified = True
