
console.log("load script.js");

function createProductCard(wrapper, data) {
    const card = document.createElement("div");
    card.className = "product-card";

    // 카드 전체를 감싸는 링크
    const link = document.createElement("a");
    link.href = data.link || "#"; // 링크가 없으면 기본적으로 #로 설정

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
    heartIcon.src = "/static/images/heart_gray.svg";
    heartIcon.alt = "Heart Icon";
    heartIcon.className = "heart-icon";
    heartIcon.dataset.recd_id = data.rcmd_id
    if (data.is_liked === true) {
        heartIcon.classList.add("active");
        heartIcon.src = "/static/images/heart_red.svg";
    }

    heartDiv.appendChild(heartIcon);

    heartIcon.addEventListener("click", (e) => {
        e.stopPropagation();
        heartIcon.classList.toggle("active");
        heartIcon.src = heartIcon.classList.contains("active")
            ? "/static/images/heart_red.svg"
            : "/static/images/heart_gray.svg";
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
            heartIcon.src = "/static/images/heart_red.svg";
        }
    });

    heartIcon.addEventListener("mouseleave", () => {
        if (!heartIcon.classList.contains("active")) {
            heartIcon.src = "/static/images/heart_gray.svg";
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
