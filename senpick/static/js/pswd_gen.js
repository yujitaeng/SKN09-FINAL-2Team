document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const nextBtn = document.querySelector(".pswd-next");

  const pw1 = document.getElementById("new-password");
  const pw2 = document.getElementById("confirm-password");

  const pw1Msg = document.getElementById("new-password-message");
  const pw2Msg = document.getElementById("confirm-password-message");

  const previousPassword = "password123";
  const pwRegex = /^(?=.*[a-z])(?=.*\d)[a-z\d]{6,15}$/;

  // 로고 클릭 → 로그인 이동
  logoBtn.addEventListener("click", () => window.location.href = "/login");

  // 🔸 새 비밀번호 입력창 클릭 시 기본 메시지 표시
  pw1.addEventListener("focus", function () {
    const val = pw1.value.trim();
    if (!pwRegex.test(val)) {
      pw1Msg.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 6~15자리";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
    }
  });

  // 🔸 새 비밀번호 입력값 변경 시 규칙 만족하면 메시지 제거
  // pw1.addEventListener("input", function () {
  //   const val = pw1.value.trim();
  //   if (pwRegex.test(val)) {
  //     pw1Msg.classList.remove("show");
  //     pw1.classList.remove("error");
  //   }
  // });
  // 🔸 새 비밀번호 입력값 변경 시 조건 검사 → 메시지 제거 또는 다시 표시
  pw1.addEventListener("input", function () {
    const val = pw1.value.trim();

    // 형식 일치
    if (pwRegex.test(val)) {
      pw1Msg.classList.remove("show");
      pw1.classList.remove("error");
    } else {
      // 형식 불일치
      pw1Msg.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 6~15자리";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
    }
  });

  // 🔸 새 비밀번호 확인창 클릭 시 불일치 시 메시지 표시
  pw2.addEventListener("focus", function () {
    if (pw1.value.trim() !== pw2.value.trim()) {
      pw2Msg.textContent = "비밀번호가 일치하지 않습니다.";
      pw2Msg.classList.add("show");
      pw2.classList.add("error");
    }
  });

  // 🔸 새 비밀번호 확인창 입력 중 일치하면 메시지 제거
  pw2.addEventListener("input", function () {
    if (pw1.value.trim() === pw2.value.trim()) {
      pw2Msg.classList.remove("show");
      pw2.classList.remove("error");
    }
  });

  // ✅ 버튼 클릭 시 모든 조건 재검사
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

    // 1. 이전 비밀번호와 동일한 경우
    if (val1 === previousPassword) {
      pw1Msg.textContent = "이전 비밀번호입니다.";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
      hasError = true;
    }

    // 2. 형식이 틀릴 경우
    else if (!pwRegex.test(val1)) {
      pw1Msg.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 6~15자리";
      pw1Msg.classList.add("show");
      pw1.classList.add("error");
      hasError = true;
    }

    // 3. 확인 비밀번호 불일치
    if (val1 !== val2) {
      pw2Msg.textContent = "비밀번호가 일치하지 않습니다.";
      pw2Msg.classList.add("show");
      pw2.classList.add("error");
      hasError = true;
    }

    // ✅ 통과
    if (!hasError) {
      window.location.href = "/login";
    }
  });
});
