document.addEventListener('DOMContentLoaded', () => {

  const path = window.location.pathname;

  // ✅ step1: 기본 회원가입 (이메일, 비밀번호, 닉네임, 약관)
  if (path.includes("signup/step1")) {
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const nickname = document.getElementById("nickname");
    const emailErr = document.getElementById("email-error");
    const pwErr = document.getElementById("password-error");
    const nickErr = document.getElementById("nickname-error");
    const termsErr = document.getElementById("terms-error");
    const requiredChk = document.querySelectorAll(".terms-box input[name=agree]");
    const allAgree = document.getElementById("allAgree");
    const nextBtn = document.getElementById("nextBtn");

    // 모달 열기
    document.querySelectorAll('[data-modal]').forEach(a => {
      a.addEventListener("dblclick", e => {
        e.preventDefault();
        const id = a.getAttribute("data-modal");
        document.getElementById(id).classList.add("open");
      });
    });

    // 모달 닫기
    document.querySelectorAll(".modal-close").forEach(btn => {
      btn.addEventListener("click", () => {
        btn.closest(".modal-overlay").classList.remove("open");
      });
    });
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
      overlay.addEventListener("click", e => {
        if (e.target === overlay) overlay.classList.remove("open");
      });
    });

    // 전체 동의 제어
    allAgree.addEventListener("change", () => {
      requiredChk.forEach(c => c.checked = allAgree.checked);
    });
    requiredChk.forEach(c => {
      c.addEventListener("change", () => {
        allAgree.checked = Array.from(requiredChk).every(ch => ch.checked);
      });
    });

    // 에러 초기화 함수
    function resetErrors() {
      [email, password, nickname].forEach(input => input.classList.remove('error'));
      [emailErr, pwErr, nickErr, termsErr].forEach(err => {
        err.style.display = "none";
        err.textContent = "";
      });
    }

    // 이메일, 비밀번호, 닉네임 정규식
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordPattern = /^[a-z0-9]{6,15}$/;
    const nicknamePattern = /^[가-힣]{1,8}$/;

    nextBtn.addEventListener("click", e => {
      e.preventDefault();
      resetErrors();
      let hasError = false;

      // 이메일 검증
      const emailValue = email.value.trim();
      if (emailValue === "") {
        emailErr.textContent = "이메일을 필수 입력해주세요.";
        emailErr.style.display = "block";
        email.classList.add("error");
        hasError = true;
      } else if (!emailPattern.test(emailValue)) {
        emailErr.textContent = "올바른 이메일 형식으로 입력해주세요.";
        emailErr.style.display = "block";
        email.classList.add("error");
        hasError = true;
      }
      /*
      else if (중복검사) {
        emailErr.textContent = "이미 가입된 이메일 입니다.";
        emailErr.style.display = "block";
        email.classList.add("error");
        hasError = true;
      }
      */

      // 비밀번호 검증 (통합 메시지)
      const pwValue = password.value.trim();
      if (pwValue === "" || !passwordPattern.test(pwValue)) {
        pwErr.textContent = "비밀번호를 입력해주세요. *영문 소문자, 숫자를 이용하여 최소 6~15자리";
        pwErr.style.display = "block";
        password.classList.add("error");
        hasError = true;
      }

      // 닉네임 검증 (통합 메시지)
      const nickValue = nickname.value.trim();
      if (nickValue === "" || !nicknamePattern.test(nickValue)) {
        nickErr.textContent = "닉네임을 입력해주세요. *한글로 최대 8자";
        nickErr.style.display = "block";
        nickname.classList.add("error");
        hasError = true;
      }
      /*
      else if (닉네임 중복검사) {
        nickErr.textContent = "이미 사용중인 닉네임입니다.";
        nickErr.style.display = "block";
        nickname.classList.add("error");
        hasError = true;
      }
      */

      // 약관 검증
      if (!Array.from(requiredChk).every(c => c.checked)) {
        termsErr.textContent = "필수 약관에 동의해주세요.";
        termsErr.style.display = "block";
        hasError = true;
      }

      if (!hasError) {
        console.log("모든 검증 통과 — 다음 단계로 이동");
        window.location.href = "/signup/step2/";
      }
    });
  }
  // ✅ step2: 이메일 인증 (5자리 입력)
  else if (path.includes("signup/step2")) {

    const inputs = document.querySelectorAll('.verify-input');
    const verifyBtn = document.getElementById("verifyBtn");

    inputs.forEach(input => {
      input.addEventListener("input", () => {
        const code = Array.from(inputs).map(i => i.value).join("");
        if (code.length === 5 && /^[0-9]{5}$/.test(code)) {
          verifyBtn.classList.add("active");
        } else {
          verifyBtn.classList.remove("active");
        }
      });
    });

    verifyBtn.addEventListener("click", () => {
      const code = Array.from(inputs).map(i => i.value).join("");
      if (code === "12345") {
        window.location.href = "/signup/step3/";
      } else {
        alert("인증번호가 일치하지 않습니다.");
      }
    });

  }

  // ✅ step3: 기본정보 입력 (생년월일, 성별, 직업)
  else if (path.includes("signup/step3")) {

    // ⏳ 여기부터 step3 검증 로직 작성 예정 자리 (비워둠)

  }

  // ✅ step4 자리 확보
  else if (path.includes("signup/step4")) {

    // ⏳ 여기부터 step4 검증 로직 작성 예정 자리 (비워둠)

  }

  // ✅ step5 자리 확보
  else if (path.includes("signup/step5")) {

    // ⏳ 여기부터 step5 검증 로직 작성 예정 자리 (비워둠)

  }
});





