from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse
import json, re
from datetime import datetime
from giftgraph.graph import gift_fsm 
from app.models import Chat, Recipient, ChatMessage, Product, ChatRecommend
from django.utils import timezone
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize the OpenAI model
llm = ChatOpenAI(
    model="gpt-4.1-nano",  # 원하는 모델로 사용 가능
    temperature=0,
)

prompt = PromptTemplate(
    input_variables=["input", "today"],
    template="""
You are an expert in language and psychology. Analyze the following conversation and respond in JSON format with:

1. "intimacy_level": 매우 낮음 / 낮음 / 보통 / 높음 / 매우 높음  
   - 기준:
     - Today is {today}
     - 평균 응답 < 10분 → 빠름
     - 마지막 메시지로부터 30일 이상 경과 → 낮음 또는 매우 낮음
     - 총 대화 기간이 1개월 미만이고 메시지 수가 적음 → 낮음
     - 하루에 20개 이상 메시지 → 높음

2. "emotional_tone": 아래 중 하나 선택  
   - 긍정적 감정 / 축하/응원 / 스트레스/위로 / 유머/친근 / 부정적 감정 / 감성/감정폭발 / 불확실/애매
3. "personality": 상대방의 성격 (e.g. 외향적, 유쾌함, 섬세함 등)  
4. "interests": 상대방의 관심사 (e.g. 영화, 여행, 음식 등)
5. "reason": 판단 근거를 **한국어**로 구체적으로 작성

If information is insufficient, return "unknown".
---

Conversation:
{input}

※ Response format (JSON only):
  "intimacy_level": "...",
  "emotional_tone": "...",
  "personality": "...",
  "interests": "...",
  "reason": "...",
""")

llm_chain = prompt | llm

def chat(request):
    if request.session.get("user_id") is None:
        return redirect('login')  # 로그인하지 않은 경우 로그인 페이지로 리디렉션
    birth = request.session.get('birth')  # 예: '19990101'

    # 오늘 날짜 → 'MMDD'만 추출
    today_mmdd = timezone.now().strftime('%m%d')

    # 생일에서 'MMDD'만 추출
    birth_mmdd = birth[4:] if birth else ''

    is_birth_today = (birth_mmdd == today_mmdd)
    
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
        
        messager_analysis = data.get("messager_analysis")
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
            "messager_analysis": messager_analysis
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
                    "brand": product_obj.brand,
                    "title": product_obj.name,
                    "imageUrl": product_obj.image_url,
                    "price": product_obj.price,
                    "link": product_obj.product_url,
                    "is_liked": recommend.is_liked,
                    "reason": product["reason"],
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

def chat_detail(request, chat_id):
    user_id = request.session.get("user_id", None)
    if user_id is None:
        return redirect('login')  # 로그인하지 않은 경우 로그인 페이지로 리디렉션
    chat = Chat.objects.filter(chat_id=chat_id, user_id=user_id).first()
    if not chat:
        return JsonResponse({"error": "Chat not found"}, status=404)
    
    messages = ChatMessage.objects.filter(chat_id=chat).order_by('created_at').values('sender', 'message', 'created_at')
    recipient = Recipient.objects.filter(chat_id=chat).first()
    
    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': list(messages),
        'recipient_info': recipient,
    })
    
def decode_utf8_escaped(s):
    return s.encode('latin1').decode('utf-8')

def normalize_message(content):
    content = content.strip()
    if '이모티콘' in content:
        return '(이모티콘)'
    if '사진' in content:
        return '(사진)'
    content = re.sub(r'(!|ㄷ|ㅎ|ㅋ|ㅠ|ㅜ|\?|헐|하|헤|호|흐|허|와우|오오|진짜){2,}', r'\1\1', content)
    content = re.sub(r'\.{3,}', '...', content)
    content = re.sub(r'http[s]?://\S+', '(링크)', content)
    content = re.sub(r'\b\d{10,14}\b', '(계좌번호)', content)
    content = re.sub(r'\b01[016789]-?\d{3,4}-?\d{4}\b', '(전화번호)', content)
    content = re.sub(r'\b(0\d{1,2}-?\d{3,4}-?\d{4})\b', '(전화번호)', content)
    content = re.sub(r'\b\d{4}-\d{4}-\d{4}-\d{4}|\d{16}\b', '(카드번호)', content)
    content = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '(이메일)', content)
    return content

@csrf_exempt
def chat_upload(request):
    if request.method == "POST":
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)
        
        file = request.FILES['file']
        if not file.name.endswith('.json') and not file.name.endswith('.txt'):
            return JsonResponse({"error": "File must be a JSON or TXT"}, status=400)

        try:
            raw_bytes = file.read()
            raw_str = raw_bytes.decode('utf-8')

            # JSON 처리
            if file.name.endswith('.json'):
                raw_chat = json.loads(raw_str)
                messages = raw_chat.get("messages", [])

                # 디코드 처리
                for msg in messages:
                    msg['sender_name'] = decode_utf8_escaped(msg['sender_name'])
                    if 'content' in msg:
                        msg['content'] = decode_utf8_escaped(msg['content'])

                # 정렬 및 그룹화
                sorted_data = sorted(messages, key=lambda x: x['timestamp_ms'])
                grouped_by_date = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

                for item in sorted_data:
                    if 'content' in item and "sent an attachment" not in item['content']:
                        timestamp = datetime.fromtimestamp(item['timestamp_ms'] / 1000.0)
                        date_str = timestamp.strftime("%Y-%m-%d")
                        time_str = timestamp.strftime("%H:%M")
                        sender = item['sender_name']  # key 없이 sender_name 그대로 사용
                        content = normalize_message(item['content'])
                        grouped_by_date[date_str][time_str][sender].append(content)

                # 포맷팅
                formatted_lines = []
                for date in sorted(grouped_by_date):
                    formatted_lines.append(f"[{date}]")
                    for time in sorted(grouped_by_date[date]):
                        for sender in grouped_by_date[date][time]:
                            merged_msg = " | ".join(grouped_by_date[date][time][sender])
                            formatted_lines.append(f"{time} - {sender}: {merged_msg}")
                    formatted_lines.append("")

                formatted_chat = "\n".join(formatted_lines).strip()

            # TXT 처리
            else:
                lines = raw_str.splitlines()
                formatted_lines = []

                for line in lines:
                    line = line.strip()
                    if line:
                        formatted_lines.append(normalize_message(line))

                formatted_chat = "\n".join(formatted_lines).strip()

            # === LLM 분석 ===
            res = llm_chain.invoke(
                {
                    "input": formatted_chat,
                    "today": datetime.now().strftime("%Y-%m-%d"),
                }
            )

            try:
                llm_result = json.loads(res.content)
            except Exception as e:
                llm_result = {
                    "intimacy_level": "unknown",
                    "emotional_tone": "unknown",
                    "personality": "unknown",
                    "interests": "unknown",
                    "reason": f"LLM parsing error: {str(e)}"
                }

            # 최종 결과 반환
            return JsonResponse({
                "message": "File uploaded and analyzed successfully",
                "llm_analysis": llm_result
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
def chat_guest_start(request):
    if request.method == "POST":
        if request.session.get("user_id") is not None:
            return redirect('chat')
        
        import uuid
        guest_user_id = uuid.uuid4().hex

        # USER 테이블에 guest 계정 insert
        from app.models import User  # 네 User 모델명에 맞게 import

        User.objects.create(
            user_id=guest_user_id,
            email=f"{guest_user_id}@guest.senpick.kr",  # 더미 이메일
            password="",  # 비회원은 password 없음
            nickname="비회원",  # 기본값
            birth="19000101",  # 기본값 (있으면 넣고 아니면 null 가능)
            gender="unknown",  # 기본값
            type="guest",  # 핵심 → guest로 명시
            is_email_verified=False
        )

        # 세션에 user_id 저장 → chat()에서도 그대로 사용 가능
        request.session["user_id"] = guest_user_id
        request.session["nickname"] = "비회원"
        request.session["type"] = "guest"  # guest 타입으로 설정

        return redirect('chat')