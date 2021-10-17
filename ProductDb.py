import csv


class ProductDb:
    def __init__(self):
        with open(f"vision_product_search_product_catalog.csv", newline='') as g:
            reader = csv.reader(g)
            self.data = list(reader)
    def get_product_by_name(self,name):
        for product in self.data:
            if product[1]==name:
                return product
    def product_search(self,word):
        products = []
        for product in self.data:
            if word in product[1]:
                products.append(product)
        return product


db = ProductDb()