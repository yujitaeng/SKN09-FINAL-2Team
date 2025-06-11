document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const nextBtn = document.querySelector(".pswd-next");
  const pw1 = document.getElementById("new-password");
  const pw2 = document.getElementById("confirm-password");
  const pw1Msg = document.getElementById("new-password-message");
  const pw2Msg = document.getElementById("confirm-password-message");

  const pwRegex = /^(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$^*()_\+\-=\[\]{}])[a-z0-9!@#$^*()_\+\-=\[\]{}]{8,15}$/;

    // 로고 클릭 → 로그인 이동
  logoBtn.addEventListener("click", () => window.location.href = "/login");
  
  // 새 비밀번호 입력창 클릭 시 기본 메시지 표시
  pw1.addEventListener("focus", function () {
    const val = pw1.value.trim();
    if (!pwRegex.test(val)) {
      pw1Msg.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 8~15자리";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
    }
  });

  // 새 비밀번호 입력값 변경 시 조건 검사
  pw1.addEventListener("input", function () {
    const val = pw1.value.trim();
    if (pwRegex.test(val)) {
      pw1Msg.classList.remove("show");
      pw1.classList.remove("error");
    } else {
      pw1Msg.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 8~15자리";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
    }
  });

  // 새 비밀번호 확인창 클릭 시 불일치 시 메시지 표시
  pw2.addEventListener("focus", function () {
    if (pw1.value.trim() !== pw2.value.trim()) {
      pw2Msg.textContent = "비밀번호가 일치하지 않습니다.";
      pw2Msg.classList.add("show");
      pw2.classList.add("error");
    }
  });

  // 새 비밀번호 확인창 입력 중 일치하면 메시지 제거
  pw2.addEventListener("input", function () {
    if (pw1.value.trim() === pw2.value.trim()) {
      pw2Msg.classList.remove("show");
      pw2.classList.remove("error");
    }
  });

  nextBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const val1 = pw1.value.trim();
    const val2 = pw2.value.trim();

    // 초기화
    pw1Msg.classList.remove("show");
    pw2Msg.classList.remove("show");
    pw1.classList.remove("error");
    pw2.classList.remove("error");

    let hasError = false;

    // 1. 형식이 틀릴 경우
    if (!pwRegex.test(val1)) {
      pw1Msg.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 8~15자리";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
      hasError = true;
    }

    // 2. 확인 비밀번호 불일치
    if (val1 !== val2) {
      pw2Msg.textContent = "비밀번호가 일치하지 않습니다.";
      pw2Msg.classList.add("show");
      pw2.classList.add("error");
      hasError = true;
    }

    if (!hasError) {
      fetch("/api/set_password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ new_password: val1 }),
      })
      .then(res => res.json())
      .then(data => {

        if (data.success) {
          window.location.href = "/login";
        } else {
          if (data.message === "이전 비밀번호입니다.") {
            pw1Msg.textContent = data.message;
            pw1Msg.classList.add("show");
            pw1.classList.add("error");
          } else {
            alert(data.message);
          }
        }
      })
      .catch(error => {
        console.error("요청 실패:", error);
        alert("비밀번호 변경 중 오류가 발생했습니다.");
      });
    }
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
