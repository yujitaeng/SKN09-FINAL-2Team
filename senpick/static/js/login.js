document.addEventListener("DOMContentLoaded", function () {
  const emailInput = document.getElementById("email");
  const emailError = document.getElementById("email-error");
  const pwInput = document.getElementById("password");
  const pwError = document.getElementById("password-error");
  const loginForm = document.querySelector(".login-form");

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
    const email = emailInput.value.trim();
    const password = pwInput.value.trim();

    emailInput.classList.remove("error");
    emailError.style.display = "none";
    pwInput.classList.remove("error");
    pwError.style.display = "none";

    let valid = true;

    if (!email) {
      emailInput.classList.add("error");
      emailError.textContent = "이메일을 입력해주세요.";
      emailError.textContent = "이메일이 올바르지 않습니다.";
      emailError.style.display = "block";
      valid = false;
    } 

    if (!password) {
      pwInput.classList.add("error");
      pwError.textContent = "비밀번호가 올바르지 않습니다.";
      pwError.style.display = "block";
      valid = false;
    } 

    if (!valid) {
      e.preventDefault(); // 폼 제출 방지
      return;
    }

    // // 서버로 AJAX 요청
    // fetch("/login/", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //     "X-CSRFToken": getCookie("csrftoken")
    //   },
    //   body: JSON.stringify({
    //     username: email,
    //     password: password
    //   })
    // })
    //   .then(res => res.json())
    //   .then(data => {
    //     if (data.success) {
    //       window.location.href = "/chat";
    //     } else {
    //       if (data.email_error) {
    //         emailInput.classList.add("error");
    //         emailError.textContent = data.email_error;
    //         emailError.style.display = "block";
    //       }
    //       if (data.password_error) {
    //         pwInput.classList.add("error");
    //         pwError.textContent = data.password_error;
    //         pwError.style.display = "block";
    //       }
    //     }
    //   })
    //   .catch(err => {
    //     console.error("로그인 요청 실패", err);
    //     pwError.textContent = "서버 통신 오류. 다시 시도해 주세요.";
    //     pwError.style.display = "block";
    //   });
  });
});
