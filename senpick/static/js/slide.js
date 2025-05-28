document.addEventListener("DOMContentLoaded", function () {
  const slider = document.getElementById("slider");
  const slides = Array.from(slider.children);
  const slideCount = slides.length;
  const slideWidth = 1032;

  // 슬라이더 전체 너비 계산
  slider.style.width = `${slideWidth * slideCount * 2}px`;
  slider.style.display = "flex";

  // 복제 슬라이드 추가 (무한 루프)
  slides.forEach(slide => {
    const clone = slide.cloneNode(true);
    slider.appendChild(clone);
  });

  let current = 0;
  const totalSlides = slideCount * 2;
  const dots = document.querySelectorAll(".dot");

  function updateIndicator(currentIndex) {
    dots.forEach((dot, idx) => {
      dot.classList.toggle("active", idx === currentIndex);
    });
  }

  setInterval(() => {
    current++;
    slider.style.transition = "transform 0.5s ease-in-out";
    slider.style.transform = `translateX(-${slideWidth * current}px)`;

    updateIndicator(current % slideCount); // 도트 업데이트

    if (current === slideCount) {
      setTimeout(() => {
        slider.style.transition = "none";
        slider.style.transform = "translateX(0px)";
        current = 0;
        updateIndicator(0);
      }, 500);
    }
  }, 5000);
});
