from app.models import ChatRecommend, Product

def get_recommended_products(chat_id):
    recommend_products = ChatRecommend.objects.filter(chat_id=chat_id)
    product_ids = recommend_products.values_list('product_id', flat=True)
    products_qs = Product.objects.filter(product_id__in=product_ids)
    products_dict = {p.product_id: p for p in products_qs}

    products = []
    for recommend in recommend_products:
        product = products_dict.get(recommend.product_id_id)
        if product:
            products.append({
                "recommend_id": recommend.rcmd_id,
                "brand": product.brand,
                "title": product.name,
                "image_url": product.image_url,
                "price": product.price,
                "product_url": product.product_url,
                "is_liked": recommend.is_liked,
            })
    return products

def update_like_status(recommend_id, is_liked):
    chat_recommend = ChatRecommend.objects.get(rcmd_id=recommend_id)
    chat_recommend.is_liked = is_liked
    chat_recommend.save()
