document.addEventListener("DOMContentLoaded", function () {
  const emailInput = document.getElementById("email");
  const emailError = document.getElementById("email-error");
  const pwInput = document.getElementById("password");
  const pwError = document.getElementById("password-error");
  const loginForm = document.querySelector(".login-form");

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const passwordPattern = /^(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$^*()_\+\-=\[\]{}])[a-z0-9!@#$^*()_\+\-=\[\]{}]{8,15}$/;

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }

  emailInput.addEventListener("focus", () => {
    if (emailInput.value.trim() === "") {
      emailInput.classList.add("error");
      emailError.style.display = "block";
    }
  });

  pwInput.addEventListener("focus", () => {
    if (pwInput.value.trim() === "") {
      pwInput.classList.add("error");
      pwError.style.display = "block";
    }
  });

  emailInput.addEventListener("blur", () => {
    if (emailInput.value.trim() !== "") {
      emailInput.classList.remove("error");
      emailError.textContent = ""; // 에러 메시지 초기화
      emailError.style.display = "none";
    }
  });

  pwInput.addEventListener("blur", () => {
    if (pwInput.value.trim() !== "") {
      pwInput.classList.remove("error");
      pwError.textContent = ""; // 에러 메시지 초기화
      pwError.style.display = "none";
    }
  });

  loginForm.addEventListener("submit", function (e) {
    let valid = true;

    // 초기화
    emailError.style.display = "none";
    pwError.style.display = "none";
    emailInput.classList.remove("error");
    pwInput.classList.remove("error");

    const email = emailInput.value.trim();
    const password = pwInput.value.trim();

    // 이메일 유효성 검사
    if (!email) {
      emailInput.classList.add("error");
      emailError.textContent = "이메일을 입력해주세요.";
      emailError.style.display = "block";
      valid = false;
    } else if (!emailPattern.test(email)) {
      emailInput.classList.add("error");
      emailError.textContent = "올바른 이메일 형식을 입력해주세요.";
      emailError.style.display = "block";
      valid = false;
    }

    // 비밀번호 유효성 검사
    if (!password || !passwordPattern.test(password)) {
      pwInput.classList.add("error");
      pwError.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자, 특수문자(!@#$^*()_+-=[]{})를 포함하여 8~15자";
      pwError.style.display = "block";
      valid = false;
    }

    // 유효성 실패 시 전송 막기
    if (!valid) {
      e.preventDefault();
    }
  });
});
