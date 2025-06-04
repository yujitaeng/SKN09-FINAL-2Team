// document.addEventListener("DOMContentLoaded", function () {
//   const emailInput = document.getElementById("email");
//   const emailError = document.getElementById("email-error");
  
//   const nextBtn = document.querySelector(".pswd-next");

// emailInput.addEventListener("focus", function () {
//   if (emailInput.value === "") {
//     emailInput.classList.add("error");
//     emailError.classList.add("show");
//     emailError.textContent = "이메일을 필수 입력해주세요.";
//   }
// });

// emailInput.addEventListener("blur", function () {
//   if (emailInput.value !== "") {
//     emailInput.classList.remove("error");
//     emailError.classList.remove("show");
//   }
// });

// nextBtn.addEventListener("click", function (e) {
//   e.preventDefault(); // 폼 제출 막기 (테스트용)
//   const email = emailInput.value.trim();

//   if (email !== "test@test.com") {
//     emailInput.classList.add("error");
//     emailError.textContent = "가입되지 않은 이메일입니다.";
//     emailError.classList.add("show");
//   } else {
//     emailInput.classList.remove("error");
//     emailError.classList.remove("show");
//   }
// });

// });

document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");

  const emailInput = document.getElementById("email");
  const emailError = document.getElementById("email-error");
  const nextBtn = document.querySelector(".pswd-next");


    // 로고 클릭 → 로그인 이동
  logoBtn.addEventListener("click", () => window.location.href = "/login");
  
  emailInput.addEventListener("focus", function () {
    if (emailInput.value === "") {
      emailInput.classList.add("error");
      emailError.classList.add("show");
      emailError.textContent = "이메일을 필수 입력해주세요.";
    }
  });

  emailInput.addEventListener("blur", function () {
    if (emailInput.value !== "") {
      emailInput.classList.remove("error");
      emailError.classList.remove("show");
    }
  });

  nextBtn.addEventListener("click", function (e) {
    e.preventDefault(); // 기본 제출 막음

    const email = emailInput.value.trim();

    if (email !== "test@test.com") {
      emailInput.classList.add("error");
      emailError.textContent = "가입되지 않은 이메일입니다.";
      emailError.classList.add("show");
    } else {
      // 에러 제거
      emailInput.classList.remove("error");
      emailError.classList.remove("show");

      // ✅ 페이지 이동
      window.location.href = "/pswd_verif"; 
    }
  });
});
