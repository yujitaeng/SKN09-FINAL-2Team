document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const emailInput = document.getElementById("email");
  const emailError = document.getElementById("email-error");
  const loginForm = document.querySelector(".login-form");
  console.log("loginform loaded:", loginForm);

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

  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();
    console.log("submit 이벤트 발생");
    const email = emailInput.value.trim();

    if (email === "") {
      emailInput.classList.add("error");
      emailError.textContent = "이메일을 필수 입력해주세요.";
      emailError.classList.add("show");
      return;
    }

    fetch("/api/pswd_request/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      credentials: "include", 
      body: JSON.stringify({ email: email })
    })
      .then((res) => {
        console.log("fetch 응답 status:", res.status);
        return res.json();
  })
      .then((data) => {
        console.log("fetch 결과:", data);
        if (data.success) {
          window.location.href = data.redirect_url;
        } else {
          console.error("서버 응답 실패:", data.message);
          emailInput.classList.add("error");
          emailError.textContent = data.message || "가입되지 않은 이메일입니다.";
          emailError.classList.add("show");
        }
      })
      .catch((err) => {
        console.error("fetch 실패:", err);
        emailInput.classList.add("error");
        emailError.textContent = "서버 요청 중 오류가 발생했습니다.";
        emailError.classList.add("show");
      });
  });

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }
});
