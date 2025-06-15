from django.contrib.auth.hashers import check_password
from app.models.user import User
from django.utils import timezone
from app.models import User
from giftgraph.graph import gift_fsm
from app.utils import extract_products_from_response

class AuthError(Exception):
    pass

def authenticate_user(email: str, password: str):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise AuthError("이메일 또는 비밀번호가 올바르지 않습니다.")
    
    if not check_password(password, user.password):
        raise AuthError("이메일 또는 비밀번호가 올바르지 않습니다.")

    return user

def initialize_user_session(request, user: User):
    request.session.flush()
    request.session["user_id"] = user.user_id
    request.session["nickname"] = user.nickname
    request.session["birth"] = user.birth
    request.session["profile_image"] = user.profile_image or ""

    today_mmdd = timezone.now().strftime('%m%d')
    birth_mmdd = user.birth[4:] if user.birth else ''
    request.session["is_birth"] = (today_mmdd == birth_mmdd)

def get_user_with_preferences(user_id):
    return User.objects.prefetch_related('preferences__prefer_type').filter(user_id=user_id).first()

def calculate_age(birth: str, current_year: int = 2025):
    if birth and len(birth) >= 4:
        birth_year = int(birth[:4])
        return current_year - birth_year
    return None

def build_gift_recommendation_state(user, age, prefer_tags):
    situation_info = {
        "closeness": "본인",
        "emotion": "축하, 기쁨",
        "preferred_style": ",".join(prefer_tags),
        "price_range": "적당한 가격",
    }

    recipient_info = {
        'gender': user.gender,
        'ageGroup': age,
        'relation': "본인",
        'anniversary': "생일",
    }

    return {
        "chat_history": [],
        "recipient_info": recipient_info,
        "situation_info": situation_info,
        "output": "",
    }

def get_birth_recommendations(user_id, current_year=2025):
    user = get_user_with_preferences(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다."

    prefer_types = user.preferences.all() if user and user.preferences.exists() else []
    prefer_tags = [prefer.prefer_type.type_name for prefer in prefer_types]
    age = calculate_age(user.birth, current_year)
    
    state = build_gift_recommendation_state(user, age, prefer_tags)
    result = gift_fsm.invoke(state)
    
    if not isinstance(result, dict):
        return [], None

    output = result.get("output", "").replace("bot: ", "")
    _, products = extract_products_from_response(output)

    recommend_products = []
    for product in products:
        if "상품명:" in product["brand"]:
            product["brand"] = ""
        recommend_products.append({
            "id": product.get("id", 0),
            "imageUrl": product.get("imageUrl", ""),
            "brand": product.get("brand", ""),
            "title": product.get("title", ""),
            "reason": product.get("reason", ""),
        })

    return recommend_products, None