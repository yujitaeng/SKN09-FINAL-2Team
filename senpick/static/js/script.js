function createProductCard(wrapper, data) {
    const card = document.createElement("div");
    card.className = "product-card";

    const link = document.createElement("a");
    link.href = data.link || "#"; // 링크가 없으면 기본적으로 #로 설정
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    // 이미지 영역
    const imageWrapper = document.createElement("div");
    imageWrapper.className = "image-wrapper";

    const image = document.createElement("img");
    image.src = data.imageUrl;
    image.alt = "상품 이미지";

    imageWrapper.appendChild(image);
    link.appendChild(imageWrapper);

    // 상품 정보
    const info = document.createElement("div");
    info.className = "product-info";

    const brand = document.createElement("div");
    brand.className = "brand";
    brand.textContent = data.brand;

    const title = document.createElement("div");
    title.className = "title";
    title.textContent = data.title;

    info.appendChild(brand);
    info.appendChild(title);
    
    // 하트 아이콘
    link.appendChild(info);

    const heartDiv = document.createElement("div");
    heartDiv.className = "heart";

    const heartIcon = document.createElement("img");
    heartIcon.src = "/static/images/Heart_gray.svg";
    heartIcon.alt = "Heart Icon";
    heartIcon.className = "heart-icon";
    heartIcon.dataset.recd_id = data.recommend_id
    if (data.is_liked === true) {
        heartIcon.classList.add("active");
        heartIcon.src = "/static/images/Heart_red.svg";
    }

    heartDiv.appendChild(heartIcon);

    heartIcon.addEventListener("click", (e) => {
        e.stopPropagation();
        hearts = document.querySelectorAll(`.heart-icon[data-recd_id='` + heartIcon.dataset.recd_id + "']");
        hearts.forEach((icon) => {
            icon.classList.toggle("active");
            icon.src = icon.classList.contains("active")
                ? "/static/images/Heart_red.svg"
                : "/static/images/Heart_gray.svg";
        })
        fetch(`/recommends/${heartIcon.dataset.recd_id}/like`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                is_liked: heartIcon.classList.contains("active")
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
    });

    heartIcon.addEventListener("mouseenter", () => {
        if (!heartIcon.classList.contains("active")) {
            heartIcon.src = "/static/images/Heart_red.svg";
        }
    });

    heartIcon.addEventListener("mouseleave", () => {
        if (!heartIcon.classList.contains("active")) {
            heartIcon.src = "/static/images/Heart_gray.svg";
        }
    });

    // 조립
    card.appendChild(link);
    card.appendChild(heartDiv);
    if (data.reason){
        const reason = document.createElement("div");
        reason.className = "reason";
        reason.textContent = "추천 이유 : " + data.reason;
        card.appendChild(reason);
    }
    wrapper.appendChild(card);
}

// 하트 아이콘 이벤트 연결 함수
function attachHeartEvents(heartIcon) {
    heartIcon.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    hearts = document.querySelectorAll(`.heart-icon[data-recd_id='` + heartIcon.dataset.recd_id + "']");
    hearts.forEach((icon) => {
        icon.classList.toggle("active");
        icon.src = icon.classList.contains("active")
            ? "/static/images/Heart_red.svg"
            : "/static/images/Heart_gray.svg";
    })
    
    fetch(`/recommends/${heartIcon.dataset.recd_id}/like`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        is_liked: heartIcon.classList.contains('active')
        })
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    });
    });

    heartIcon.addEventListener('mouseenter', () => {
    if (!heartIcon.classList.contains('active')) {
        heartIcon.src = '/static/images/Heart_red.svg';
    }
    });

    heartIcon.addEventListener('mouseleave', () => {
    if (!heartIcon.classList.contains('active')) {
        heartIcon.src = '/static/images/Heart_gray.svg';
    }
    });
}

function toggleLikeBlock(cardEl) {
    const likeBlock = cardEl.closest('.like-block');
    const scrollWrapper = likeBlock.querySelector('.product-scroll-wrapper');
    const cardWrapper = likeBlock.querySelector('.card-wrapper');
    const likeCount = likeBlock.querySelector('.like-count');

    const isOpen = likeBlock.classList.contains('active');
    if (isOpen) {
        scrollWrapper.classList.add('hidden');
        likeBlock.classList.remove('active');
    } else {
        scrollWrapper.classList.remove('hidden');
        likeBlock.classList.add('active');

        if (cardWrapper.children.length === 0) {
            const chatId = likeBlock.dataset.chat_id;
            const products = window.productMap?.[chatId] || [];

            products.forEach(product => createProductCard(cardWrapper, product));
            likeCount.innerText = `💛 ${products.length}`;
        }
    }
}

// 채팅 리스트 렌더링 함수
function renderChatList(chatList) {
    chatHistoryEl.innerHTML = '';  // 기존 목록 초기화
    const chatFormEl = document.getElementById('chat-form');
    window.currentChatId = chatFormEl ? chatFormEl.dataset.chatId : null;
    chatList.forEach(chat => {
        const li = document.createElement('li');
        const span = document.createElement('span');
        span.className = 'chat-title';
        span.textContent = chat.title;

        // chat_id 를 dataset 으로 저장 (클릭 시 사용 가능)
        li.dataset.chatId = chat.chat_id;
        if (li.dataset.chatId === window.currentChatId) {
        li.classList.add('selected'); // 현재 선택된 채팅에 selected 클래스 추가
        }

        li.appendChild(span);

        // 선택 시 selected 클래스 토글
        li.addEventListener('click', () => {
        document.querySelector('.chat-list li.selected')?.classList.remove('selected');
        li.classList.add('selected');

        // 필요시 chat_id 를 활용해서 채팅 불러오기 등 추가 동작 가능
        console.log('Selected chat_id:', li.dataset.chatId);
        window.currentChatId = li.dataset.chatId; // 현재 선택된 chat_id 저장
        window.location.href = `/chat/${li.dataset.chatId}`; // 채팅 페이지로 이동
        });

        chatHistoryEl.appendChild(li);
    });
}