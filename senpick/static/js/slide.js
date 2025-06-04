document.addEventListener("DOMContentLoaded", function () {
  const slider = document.getElementById('slider');
  // const slides = document.querySelectorAll('.slide-content');
  const slides = document.querySelectorAll('.slider-wrapper .slide-content');
  // const dots = document.querySelectorAll('.dot');
  const dots   = document.querySelectorAll('.slide-indicator .dot');
  const slideCount = slides.length;
  const slideWidth = slides[0].offsetWidth;

  let currentIndex = 0;
  let isTransitioning = false;

  // 🔁 슬라이드 복제
  const cloneFirst = slides[0].cloneNode(true);
  slider.appendChild(cloneFirst);

  function goToSlide(index) {
    if (isTransitioning) return;
    isTransitioning = true;

    slider.style.transition = 'transform 1s ease';
    slider.style.transform = `translateX(-${slideWidth * index}px)`;

    // dot 처리
    dots.forEach(dot => dot.classList.remove('active'));
    dots[index % slideCount].classList.add('active');

    // 🔄 5 → 1 복제 슬라이드 도달 후 트릭
    if (index === slideCount) {
      setTimeout(() => {
        slider.style.transition = 'none'; // 트랜지션 없이 순간이동
        slider.style.transform = 'translateX(0px)';
        currentIndex = 0;
        isTransitioning = false;
      }, TRANSITION_DURATION_MS); // 트랜지션 시간과 맞춰야 함
    } else {
      setTimeout(() => {
        isTransitioning = false;
      }, TRANSITION_DURATION_MS);
    }
  }

  function autoSlide() {
    currentIndex++;
    goToSlide(currentIndex);
  }

  // 초기 세팅
  goToSlide(currentIndex);
  setInterval(autoSlide, 5000);
});
