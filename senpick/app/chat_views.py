from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse
import json, re
from giftgraph.graph import gift_fsm 
from app.models import Chat, Recipient, ChatMessage, Product, ChatRecommend
from django.utils import timezone

def chat(request):
    if request.session.get("user_id") is None:
        return redirect('login')  # 로그인하지 않은 경우 로그인 페이지로 리디렉션
    birth = request.session.get('birth')  # 예: '19990101'
    
    # 오늘 날짜 구하기 → 'YYYYMMDD' 형식으로 변환
    today_str = timezone.now().strftime('%Y%m%d')
    
    is_birth_today = (birth == today_str)
    return render(request, 'chat.html', {
        'is_birth_today': is_birth_today,
    })

def get_state(request):
    return request.session.get("chat_state", {
        "chat_history": [],
        "situation_info": {
            "closeness": "",
            "emotion": "",
            "preferred_style": "",
            "price_range": ""
        },
        "recipient_info": {
            'gender': "",
            'ageGroup': "",
            'relation': "",
            'anniversary': "",
        }
    })

def save_state(request, state):
    request.session["chat_state"] = state
    request.session.save()
    
def extract_products_from_response(data):
    # 상품 블록 분리
    data = re.split(r'\n\d+\.\s*', data.strip())
    msg = data[0]
    blocks = data[1:]

    # JSON 배열 구성
    items = []
    for idx, block in enumerate(blocks):
        brand = re.search(r'-\s*\*?\s*\*?\s*브랜드\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)
        name = re.search(r'-\s*\*?\s*\*?\s*상품명\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)
        price = re.search(r'-\s*\*?\s*\*?\s*가격\s*\*?\s*\*?\s*:\s*₩\s*([\d,]+)', block).group(1)
        # 이미지 robust 패턴
        image_match = re.search(
            r'-\s*\*?\s*\*?\s*이미지\s*\*?\s*\*?\s*:\s*(?:!\[.*?\]\(\s*(.*?)\s*\)|(\S+))',
            block
        )
        image = image_match.group(1) or image_match.group(2) if image_match else None

        # 링크 robust 패턴
        link_match = re.search(
            r'-\s*\*?\s*\*?\s*링크\s*\*?\s*\*?\s*:\s*(?:\[.*?\]\(\s*(.*?)\s*\)|(\S+))',
            block
        )
        link = link_match.group(1) or link_match.group(2) if link_match else None

        reason = re.search(r'-\s*\*?\s*\*?\s*추천\s*이유\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)

        items.append({
            # "id": len(st.session_state.all_products) + idx,
            "brand": brand,
            "title": name,
            "price": price,
            "imageUrl": image,
            "link": link,
            "reason": reason
        })

    return msg, items

@csrf_exempt
def chat_start(request):
    if request.method == "POST":
        request.session.pop("chat_state", None)

        data = json.loads(request.body)
       
        situation_info = {
            "closeness": "",
            "emotion": "",
            "preferred_style": "",
            "price_range": "",
        }
        
        recipient_info = {
            'gender': data.get("gender", ""),
            'ageGroup': data.get("age", ""),
            'relation': data.get("relation", ""),
            'anniversary': data.get("event", ""),
        }
        # insert recipient_info into db recipient table
        chat_obj = Chat.objects.create(
            user_id=request.session.get("user_id", None),
            title=f"{recipient_info['relation']}를 위한 선물",
        )  # 채팅 시작 시 새로운 Chat 객체 생성
        recipient = Recipient.objects.create(
            chat_id=chat_obj,
            gender=recipient_info["gender"],
            age_group=recipient_info["ageGroup"],
            relation=recipient_info["relation"],
            anniversary=recipient_info["anniversary"],
            situation_info=json.dumps(situation_info)  # 상황 정보는 JSON 문자열로 저장
        )
        
        state = {
            "chat_history": [],
            "situation_info": situation_info,
            "recipient_info": recipient_info, 
        }
        
        request.session["chat_state"] = state  # 초기 상태 저장
        
        # 스트림 처리 
        res = gift_fsm.invoke(state)
        
        if isinstance(res, dict):
            state = res
            output = res.get("output", "")
            state["chat_history"].append(f"bot: {output}")
            request.session["chat_state"] = state
        else:  # 만약 res가 dict가 아니라면, 단순 문자열로 처리
            # 스트림 처리 
            output = ""
            for chunk in res:
                output += chunk
            state["output"] = output
            state["chat_history"].append(f"bot: {output}")
            request.session["chat_state"] = state
        ChatMessage.objects.create(
            chat_id=chat_obj,
            sender="bot",
            message=output
        )
        save_state(request, state)
        return JsonResponse({"bot": output, "chat_id": chat_obj.chat_id})
    return JsonResponse({"error": "POST only"})

@csrf_exempt
def chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg = data["message"]
        chat_id = data["chat_id"]  # 클라이언트가 보내는 chat_id 사용
        # chat_id로 Chat 인스턴스 가져오기
        chat_obj = Chat.objects.get(chat_id=chat_id)
        state = get_state(request)
        
        state["chat_history"].append(f"user: {msg}")
        ChatMessage.objects.create(
            chat_id=chat_obj,
            sender="user",
            message=msg
        )

        res = gift_fsm.invoke(state)

        if isinstance(res, dict):
            state = res
            situation_info = state.get("situation_info", {})
            output = state.get("output", "")
            ChatMessage.objects.create(
                chat_id=chat_obj,
                sender="bot",
                message=output
            )
            if situation_info:
                Recipient.objects.filter(chat_id=chat_obj).update(
                    situation_info=json.dumps(situation_info)
                )
            output, products = extract_products_from_response(output)
            recommend_produsts = []
            for product in products:
                product_obj, created = Product.objects.get_or_create(
                    name=product["title"],
                    defaults={
                        "brand": product["brand"],
                        "price": int(product["price"].replace(",", "").replace("₩", "").strip()),
                        "image_url": product["imageUrl"],
                        "product_url": product["link"],
                    }
                )
                recommend = ChatRecommend.objects.create(
                    chat_id=chat_obj,
                    product_id=product_obj,
                )
                recommend_produsts.append({
                    "recommend_id": recommend.rcmd_id,
                    "title": product_obj.name,
                    "image_url": product_obj.image_url,
                    "price": product_obj.price,
                    "product_url": product_obj.product_url,
                    "is_liked": recommend.is_liked,
                })
                
            output = output.split("Final Answer:")[1].strip() if "Final Answer:" in output else output
            
        else:  
            def stream():
                output_parts = []
                for chunk in res:
                    output_parts.append(chunk)
                    yield chunk  # str or bytes 확인 필요
                
                # 최종 출력 누적해서 chat_history 에 기록
                output = "".join(output_parts)
                state["output"] = output
                state.get("chat_history").append(f"bot: {output}")
                ChatMessage.objects.create(
                    chat_id=chat_obj,
                    sender="bot",
                    message=output
                )
                request.session["chat_state"] = state
                request.session.save()
    
            return StreamingHttpResponse(stream(), content_type='text/plain')

        save_state(request, state if isinstance(res, dict) else state)
        return JsonResponse({"bot": output, "products": recommend_produsts})
    return JsonResponse({"error": "POST only"})

def chat_history(request):
    chats = Chat.objects.filter(user_id=request.session.get("user_id", None)) \
                        .order_by('-created_at') \
                        .values('chat_id', 'title', 'created_at')
    return JsonResponse({"chatlist": list(chats)})