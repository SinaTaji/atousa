from products.models import ProductVariant

Cart_Session_Id = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(Cart_Session_Id)
        if not cart:
            cart = self.session[Cart_Session_Id] = {}
        self.cart = cart

    def __iter__(self):
        product_variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=product_variant_ids).select_related('product', 'color', 'size')

        cart = self.cart.copy()
        for variant in variants:
            key = str(variant.id)
            item = cart.get(key)

            if item:
                item['variant_id'] = variant.id
                item['variant_stock'] = variant.stock
                item['product_title'] = variant.product.title
                item['product_url'] = variant.product.get_absolute_url()
                item['product_model'] = variant.product.model
                item['product_code'] = variant.product.code
                item['color_name'] = variant.color.title if variant.color else ""
                item['size_name'] = variant.size.title if variant.size else ""
                item['price'] = variant.price
                item['variant_image_url'] = variant.image.url if variant.image else ""
                item['has_discount'] = variant.has_discount
                item['get_discounted_price'] = variant.get_discounted_price()
                item['discount'] = variant.discount
                item['item_discount'] = variant.how_mutch_discounted()
                item['total_discount'] = item['item_discount'] * int(item['quantity'])
                item['total_price'] = item['get_discounted_price'] * int(item['quantity'])

                yield item

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
        self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def total(self):
        total = 0
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids)

        for variant in variants:
            key = str(variant.id)
            quantity = self.cart.get(key, {}).get('quantity', 0)
            total += variant.get_discounted_price() * int(quantity)
        return total

    def get_total_price(self):
        total = 0
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids)

        for variant in variants:
            key = str(variant.id)
            quantity = self.cart.get(key, {}).get('quantity', 0)
            total += variant.get_discounted_price() * int(quantity)
        gift = self.session.get('gift')
        if gift:
            percent = gift.get('percent', 0)
            discount_amount = round(total * (percent / 100))
            total -= discount_amount
        return total

    def get_total_org_price(self):
        total = 0
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids)

        for variant in variants:
            key = str(variant.id)
            quantity = self.cart.get(key, {}).get('quantity', 0)
            total += variant.price * int(quantity)

        return total

    def get_total_discount(self):
        total = 0
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids)

        for variant in variants:
            key = str(variant.id)
            quantity = self.cart.get(key, {}).get('quantity', 0)
            total += variant.how_mutch_discounted() * int(quantity)
        gift = self.session.get('gift')
        if gift:
            price = self.total()
            percent = gift.get('percent', 0)
            discount_amount = (price * (percent / 100))
            total += discount_amount
        return total

    def send_free(self):
        method = self.session.get('shipping_method', 'pishteaz')
        if method == 'tipax':
            return ''
        total_price = self.get_total_price()
        to_free = 2_000_000
        remaining = to_free - total_price
        return max(0, remaining)

    def get_price_post(self):
        return self.get_total_price() + 69000

    def save(self):
        self.session.modified = True
