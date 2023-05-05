import pickle

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from store.models import Product


# ID : {QUANTITY, PRICE}
class Cart:

    def __init__(self):
        self.cart_dict = dict()

    def add(self, _id: int, quantity: int):
        product = Product.objects.filter(id=_id)[0]
        if product:
            self.cart_dict[_id] = {"quantity": quantity, "price": product.price}

    def delete(self, _id: int):
        try:
            self.cart_dict.pop(_id)
        except Exception as ex:
            print(ex)

    def update(self, _id, action, quantity):
        try:
            if action == "PLUS":
                self.cart_dict[_id]["quantity"] = self.cart_dict[_id]["quantity"] + quantity
            elif action == "MINUS":
                if self.cart_dict[_id]["quantity"] - quantity > 0:
                    self.cart_dict[_id]["quantity"] = self.cart_dict[_id]["quantity"] - quantity
                else:
                    self.delete(_id)
        except Exception as ex:
            print(ex)

    def is_exist(self, _id: int):
        return True if _id in self.cart_dict else False

    def get_dict(self):
        return self.cart_dict

    # Костыль
    def get_products_with_price(self):
        products_with_price = dict()
        for key, item in self.cart_dict.items():
            product = get_object_or_404(Product, pk=key)
            products_with_price[product] = item
        return products_with_price

    def get_size(self):
        return len(self.cart_dict)

    def get_total(self):
        total = 0
        for key, item in self.cart_dict.items():
            product = get_object_or_404(Product, pk=key)
            total = total + (product.price * item["quantity"])
        return total

    def hex_decode(self, input_hex):
        try:
            self.cart_dict = pickle.loads(bytes.fromhex(input_hex))
        except Exception as ex:
            print(ex)
            self.cart_dict = dict()

    def hex_encode(self):
        output = pickle.dumps(self.cart_dict).hex()
        return output

    def __str__(self):
        return self.cart_dict.__str__()


def cart_handler(request):
    request_data = request.GET
    cart_hex = request.session.get('cart')
    cart = Cart()
    cart.hex_decode(cart_hex)
    action = request_data.get('action')
    response = dict()
    response['status'] = False
    try:
        product_id = int(request_data.get('product_id', None))
    except:
        print("except")
    if action == "ADD":
        is_product = Product.objects.filter(id=product_id).exists()
        if is_product:
            cart.add(product_id, 1)
            response['status'] = True
    elif action == "DELETE":
        is_product = Product.objects.filter(id=product_id).exists()
        if is_product:
            cart.delete(product_id)
            response['status'] = True
    elif action == "UPDATE":
        is_product = Product.objects.filter(id=product_id).exists()
        if is_product:
            quantity = int(request_data.get('quantity'))
            cart.update(product_id, request.GET.get('act'), quantity)
            response['status'] = True

    request.session['cart'] = cart.hex_encode()
    response['cart'] = cart.get_dict()
    return JsonResponse(response)
