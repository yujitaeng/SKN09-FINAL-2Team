import os, re, boto3, random, json
from uuid import uuid4
from django.conf import settings
from django.core.mail import send_mail

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

def extract_products_from_response(data):
    # JSON 형식 응답 감지 및 파싱
    pattern = r"Final Answer:\s*(.*?)\s*\["
    match = re.search(pattern, data, re.DOTALL)
    if match:
        msg = match.group(1).strip()
    else:
        msg = data.split('[')[0].replace("Final Answer:", "").strip()
    json_match = re.search(r'\[\s*{.*?}\s*\]', data, re.DOTALL)
    if json_match:
        try:
            products_json = json.loads(json_match.group(0))
            items = []
            for prod in products_json:
                items.append({
                    "brand": prod.get("BRAND", ""),
                    "title": prod.get("NAME", ""),
                    "price": prod.get("PRICE", ""),
                    "imageUrl": prod.get("IMAGE", ""),
                    "product_url": prod.get("LINK", ""),
                    "reason": prod.get("REASON", ""),
                })
            return msg, items
        except Exception as e:
            print("[JSON 파싱 실패]", e)

    # 기존 markdown 블록 fallback 처리
    data = re.split(r'\n\d+\.\s*', data.strip())
    msg = data[0]
    blocks = data[1:]

    items = []
    for idx, block in enumerate(blocks):
        try:
            brand = re.search(r'-\s*\*?\s*\*?\s*브랜드\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)
            name = re.search(r'-\s*\*?\s*\*?\s*상품명\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)
            price = re.search(r'-\s*\*?\s*\*?\s*가격\s*\*?\s*\*?\s*:\s*₩\s*([\d,]+)', block).group(1)
            image_match = re.search(
                r'-\s*\*?\s*\*?\s*이미지\s*\*?\s*\*?\s*:\s*(?:!\[.*?\]\(\s*(.*?)\s*\)|(\S+))', block
            )
            image = image_match.group(1) or image_match.group(2) if image_match else None

            link_match = re.search(
                r'-\s*\*?\s*\*?\s*링크\s*\*?\s*\*?\s*:\s*(?:\[.*?\]\(\s*(.*?)\s*\)|(\S+))', block
            )
            product_url = (link_match.group(1) or link_match.group(2))  if link_match else None

            reason = re.search(r'-\s*\*?\s*\*?\s*추천\s*이유\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)

            items.append({
                "brand": brand,
                "title": name,
                "price": price,
                "imageUrl": image,
                "product_url": product_url,
                "reason": reason
            })
        except:
            continue

    return msg, items

def send_pswd_verification_code(request, email):
    code = ''.join([str(random.randint(0, 9)) for _ in range(5)])

    subject = "[Senpick] 비밀번호 찾기 인증 코드 안내"
    message = f"Senpick 비밀번호 찾기 인증 번호는 [{code}] 입니다.\n\n해당 번호를 인증번호 입력란에 입력해 주세요."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

    request.session['verification_code'] = code
    request.session['verification_email'] = email
    request.session.set_expiry(500)
    request.session.modified = True
    
    print(code)

    return code

def upload_to_s3(uploaded_file):
    if uploaded_file:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        filename = f"profile_images/{uuid4().hex}{ext}"

        s3.upload_fileobj(
            uploaded_file,
            "senpickbucket",
            filename,
            ExtraArgs={"ContentType": uploaded_file.content_type}
        )

        s3_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{filename}"  # 또는 직접 구성
        return s3_url
    return None