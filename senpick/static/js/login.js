document.addEventListener("DOMContentLoaded", function () {
  const emailInput = document.getElementById("email");
  const emailError = document.getElementById("email-error");
  const pwInput = document.getElementById("password");
  const pwError = document.getElementById("password-error");
  
  const loginBtn = document.querySelector(".login-btn");

  // 포커스 시 → 값이 비어있을 경우에만 에러 표시
  emailInput.addEventListener("focus", function () {
    if (emailInput.value === "") {
      emailInput.classList.add("error");
      emailError.style.display = "block";
    }
  });

  pwInput.addEventListener("focus", function () {
    if (pwInput.value === "") {
      pwInput.classList.add("error");
      pwError.style.display = "block";
    }
  });

  // 포커스 빠졌을 때 → 값이 있다면 에러 제거
  emailInput.addEventListener("blur", function () {
    if (emailInput.value !== "") {
      emailInput.classList.remove("error");
      emailError.style.display = "none";
    }
  });

  pwInput.addEventListener("blur", function () {
    if (pwInput.value !== "") {
      pwInput.classList.remove("error");
      pwError.style.display = "none";
    }
  });

  loginBtn.addEventListener("click", function (e) {
    e.preventDefault(); // 폼 제출 막기 (테스트용)

    const email = emailInput.value.trim();
    const password = pwInput.value.trim();

    let valid = true;

    if (email !== "test@test.com") {
      emailInput.classList.add("error");
      emailError.textContent = "이메일이 올바르지 않습니다.";
      emailError.style.display = "block";
      valid = false;
    } else {
      emailInput.classList.remove("error");
      emailError.style.display = "none";
    }

    if (password !== "1234") {
      pwInput.classList.add("error");
      pwError.textContent = "비밀번호가 올바르지 않습니다.";
      pwError.style.display = "block";
      valid = false;
    } else {
      pwInput.classList.remove("error");
      pwError.style.display = "none";
    }

    if (valid) {
      alert("로그인 성공 (가짜 로직)");
      // 실제 백 연결 시 여기에 form.submit() 추가
    }
  });
});
