console.log("자바스크립트 테스트")

function createProductCard(data) {
    const wrapper = document.querySelector(".card-wrapper:last-child");

    const card = document.createElement("div");
    card.className = "product-card";

    // 카드 전체를 감싸는 링크
    const link = document.createElement("a");
    link.href = "#";

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
    
    link.appendChild(info);

    // 하트 아이콘
    const heartDiv = document.createElement("div");
    heartDiv.className = "heart";

    const heartIcon = document.createElement("img");
    heartIcon.src = "/static/images/heart_gray.svg";
    heartIcon.alt = "Heart Icon";
    heartIcon.className = "heart-icon";

    heartDiv.appendChild(heartIcon);

    heartIcon.addEventListener("click", (event) => {
        event.stopPropagation();
        heartIcon.classList.toggle("active");
        heartIcon.src = heartIcon.classList.contains("active") ?
            "/static/images/heart_red.svg" :
            "/static/images/heart_gray.svg";
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
        reason.textContent = data.reason;
        card.appendChild(reason);
    }
    wrapper.appendChild(card);
}