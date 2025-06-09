from django.shortcuts import render
from django.http import JsonResponse

def birth(request):
    return render(request, 'birth.html')

def birth_recommend_products(request):
    return JsonResponse({
        'products': [
            {
                'id': 1,
                'imageUrl': 'https://shop-phinf.pstatic.net/20250317_133/1742177290390KwLPy_JPEG/6979889503620148_1772200239.jpg?type=m510',
                'brand': '브랜드명',
                'title': '삼성공식파트너 JBL FLIP6 휴대용 캠핑 피크닉 무선...',
                'reason': '추천 이유: 이 제품은 휴대성이 뛰어나고, 캠핑이나 피크닉에 적합한 무선 스피커입니다. JBL의 품질을 믿을 수 있어요.',
            },
            {
                'id': 2,
                'imageUrl': 'https://shop-phinf.pstatic.net/20250317_133/1742177290390KwLPy_JPEG/6979889503620148_1772200239.jpg?type=m510',
                'brand': '브랜드명',
                'title': '삼성공식파트너 JBL FLIP6 휴대용 캠핑 피크닉 무선...',
                'reason': '추천 이유: 이 제품은 휴대성이 뛰어나고, 캠핑이나 피크닉에 적합한 무선 스피커입니다. JBL의 품질을 믿을 수 있어요.',
            },
            {
                'id': 3,
                'imageUrl': 'https://shop-phinf.pstatic.net/20250317_133/1742177290390KwLPy_JPEG/6979889503620148_1772200239.jpg?type=m510',
                'brand': '브랜드명',
                'title': '삼성공식파트너 JBL FLIP6 휴대용 캠핑 피크닉 무선...',
                'reason': '추천 이유: 이 제품은 휴대성이 뛰어나고, 캠핑이나 피크닉에 적합한 무선 스피커입니다. JBL의 품질을 믿을 수 있어요.',
            },
            {
                'id': 4,
                'imageUrl': 'https://shop-phinf.pstatic.net/20250317_133/1742177290390KwLPy_JPEG/6979889503620148_1772200239.jpg?type=m510',
                'brand': '브랜드명',
                'title': '삼성공식파트너 JBL FLIP6 휴대용 캠핑 피크닉 무선...',
                'reason': '추천 이유: 이 제품은 휴대성이 뛰어나고, 캠핑이나 피크닉에 적합한 무선 스피커입니다. JBL의 품질을 믿을 수 있어요.',
            },
        ]
    })