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

    // 1) DOM 요소 참조
    const inputs    = document.querySelectorAll('.verify-input');   // 5칸 입력박스
    const verifyBtn = document.getElementById('verifyBtn');         // "이메일 인증 완료" 버튼
    const timerEl   = document.querySelector('.timer-text');        // "05:00" 표시 스팬
    const errorMsg  = document.querySelector('.error-message');     // 에러 메시지 출력 영역
    const resendEl  = document.querySelector('.resend-code');       // 재전송 텍스트

    // 2) 타이머 초기화 및 카운트다운 시작 (5분 = 300초)
    let timeLeft = 300;  // 300초 (5*60)
    timerEl.textContent = formatTime(timeLeft);  // 초기값 "05:00"

    const countdown = setInterval(() => {
      timeLeft--;
      if (timeLeft < 0) {
        // 1) 타이머 멈추기
        clearInterval(countdown);
        timerEl.textContent = '00:00';

        // 2) 입력박스 전체를 에러 상태로 표시
        inputs.forEach(i => i.classList.add('error'));
        // 3) 에러 메시지 변경 및 보이기
        errorMsg.textContent = '인증 시간이 만료되었습니다. 인증번호 재전송 후 다시 시도 부탁드립니다.';
        errorMsg.style.display = 'block';

        return;
      }
      timerEl.textContent = formatTime(timeLeft);
    }, 1000);

    // 시:분 형식으로 변환하는 헬퍼 함수
    function formatTime(seconds) {
      const m = Math.floor(seconds / 60).toString().padStart(2, '0');
      const s = (seconds % 60).toString().padStart(2, '0');
      return `${m}:${s}`;
    }

    // 3) 인증번호 입력박스(5칸) 제어: 숫자만 허용 + 다음칸 자동 포커스
    inputs.forEach((input, idx) => {
      input.addEventListener('input', (e) => {
        // 숫자 이외 문자는 제거
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
        if (e.target.value.length > 1) {
          e.target.value = e.target.value.slice(0, 1);
        }
        // 한 칸 입력하면 다음 칸으로 포커스 이동
        if (e.target.value && idx < inputs.length - 1) {
          inputs[idx + 1].focus();
        }
      });

      // 백스페이스 시 이전 칸으로 포커스 이동
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !e.target.value && idx > 0) {
          inputs[idx - 1].focus();
        }
      });
    });

    // 4) “이메일 인증 완료” 버튼 클릭 이벤트
    verifyBtn.addEventListener('click', () => {
      const code = Array.from(inputs).map(i => i.value).join('');
      // 예시: 서버 검증 대신 “12345”와 비교
      if (code === '12345') {
        window.location.href = '/signup/step3/';
      } else {
        // 틀린 경우: 입력박스 전체 빨간 테두리 + 에러 메시지 출력
        inputs.forEach(i => i.classList.add('error'));
        errorMsg.textContent = '인증번호가 일치하지 않습니다.';
        errorMsg.style.display = 'block';
        // 2초 뒤 초기화
        setTimeout(() => {
          inputs.forEach(i => i.classList.remove('error'));
          errorMsg.style.display = 'none';
        }, 2000);
      }
    });

    // 5) “인증코드 재전송” 클릭 이벤트
    //    • 항상 활성화 상태이므로 단순히 alert 예시만 보여줍니다.
    //    • 원하시면 이곳에 AJAX나 fetch를 이용해 서버에 재전송 요청을 날려주세요.
    resendEl.addEventListener('click', () => {
      // 재전송 시 기존 에러 메시지/빨간 테두리 모두 초기화
      inputs.forEach(i => i.classList.remove('error'));
      errorMsg.style.display = 'none';

      // 타이머 다시 5분 초기화 후 카운트다운 재시작
      clearInterval(countdown);
      timeLeft = 300;
      timerEl.textContent = formatTime(timeLeft);
      const newCountdown = setInterval(() => {
        timeLeft--;
        if (timeLeft < 0) {
          clearInterval(newCountdown);
          timerEl.textContent = '00:00';
          // 만료 시 다시 에러 출력을 원하신다면 아래 로직을 활용하세요.
          inputs.forEach(i => i.classList.add('error'));
          errorMsg.textContent = '인증 시간이 만료되었습니다. 인증번호 재전송 후 다시 시도 부탁드립니다.';
          errorMsg.style.display = 'block';
          return;
        }
        timerEl.textContent = formatTime(timeLeft);
      }, 1000);

      // 예시: 실제 서비스에서는 서버에 재전송 API 호출합니다.
      alert('새로운 인증코드를 이메일로 발송했습니다.');
    });
  }


  // ✅ step3: 기본정보 입력 (생년월일, 성별, 직업)
  else if (path.includes("signup/step3")) {

    // 1) DOM 요소 참조
    const birthEl       = document.getElementById("birth");
    const birthErrEl    = document.getElementById("birth-error");
    const maleBtn       = document.getElementById("maleBtn");
    const femaleBtn     = document.getElementById("femaleBtn");
    const genderErrEl   = document.getElementById("gender-error");
    const jobSelect     = document.getElementById("job");
    const jobErrEl      = document.getElementById("job-error");
    const nextBtn       = document.getElementById("nextBtn");

    let selectedGender = "";  // "male" 또는 "female"

    // 2) 성별 버튼 클릭 시 .selected 토글
    function selectGender(gender) {
      selectedGender = gender;
      if (gender === "male") {
        maleBtn.classList.add("selected");
        femaleBtn.classList.remove("selected");
      } else {
        femaleBtn.classList.add("selected");
        maleBtn.classList.remove("selected");
      }
    }
    maleBtn.addEventListener("click", () => {
      selectGender("male");
      genderErrEl.style.display = "none";  // 에러 메시지 숨기기
    });
    femaleBtn.addEventListener("click", () => {
      selectGender("female");
      genderErrEl.style.display = "none";
    });

    // 3) “다음 단계” 버튼 클릭 시 검증
    nextBtn.addEventListener("click", (e) => {
      e.preventDefault();

      let hasError = false;

      // 3-1) 생년월일 검증: 8자리 숫자(YYYYMMDD)
      const birthValue = birthEl.value.trim();
      // 정규식: 4자리 연도(1900~2099 가정) + 2자리 월(01~12) + 2자리 일(01~31, 간단 체크)
      const birthPattern = /^(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$/;
      if (!birthPattern.test(birthValue)) {
        birthErrEl.textContent = "생년월일이 올바르지 않습니다. (숫자만 8자리 입력)";
        birthErrEl.style.display = "block";
        birthEl.classList.add("error");
        hasError = true;
      } else {
        birthErrEl.style.display = "none";
        birthEl.classList.remove("error");
      }

      // 3-2) 성별 검증: 반드시 남자 or 여자 버튼 중 하나 선택
      if (selectedGender === "") {
        genderErrEl.textContent = "성별을 선택해주세요.";
        genderErrEl.style.display = "block";
        hasError = true;
      } else {
        genderErrEl.style.display = "none";
      }

      // 3-3) 직업 검증: 값이 빈 문자열이 아닌지
      const jobValue = jobSelect.value;
      if (jobValue === "") {
        jobErrEl.textContent = "직업을 선택해주세요.";
        jobErrEl.style.display = "block";
        jobSelect.classList.add("error");
        hasError = true;
      } else {
        jobErrEl.style.display = "none";
        jobSelect.classList.remove("error");
      }

      // 3-4) 모든 검증 통과 시 다음 단계로 이동
      if (!hasError) {
        window.location.href = "/signup/step4/";
      }
      if (!hasError) {
      // ← 여기가 “검증 통과 시 이동시키는 부분”입니다!
      window.location.href = "/signup/step4/";
    }
    });

    // 4) 입력값이 변경되면 에러 표시 제거(실시간 UX 개선)
    birthEl.addEventListener("input", () => {
      birthErrEl.style.display = "none";
      birthEl.classList.remove("error");
    });
    jobSelect.addEventListener("change", () => {
      jobErrEl.style.display = "none";
      jobSelect.classList.remove("error");
    });
  }

  // ✅ step4 자리 확보
  // signup.js 파일 중에서 Step 4 블록을 아래 코드로 반드시 덮어쓰기 해 주세요.
else if (path.includes("signup/step4")) {
  // 1) DOM 요소 참조
  const styleButtons     = document.querySelectorAll('.style-group .option-btn');
  const categoryButtons  = document.querySelectorAll('.category-group .option-btn');
  const styleErrorEl     = document.getElementById('style-error');
  const categoryErrorEl  = document.getElementById('category-error');
  const completeBtn      = document.getElementById('completeBtn');

  let selectedStyles     = []; // 최대 3개 저장
  let selectedCategories = []; // 최대 3개 저장

  // 2) “선호 스타일” 버튼 클릭 핸들링
  styleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const value = btn.dataset.value;
      const idx   = selectedStyles.indexOf(value);

      if (idx > -1) {
        // 이미 선택된 상태 → 선택 해제
        selectedStyles.splice(idx, 1);
        btn.classList.remove('selected');
      } else if (selectedStyles.length < 3) {
        // 최대 3개 미만이면 선택 추가
        selectedStyles.push(value);
        btn.classList.add('selected');
      } else {
        // 3개 이미 선택된 상태에서 4번째 클릭 시 에러
        styleErrorEl.textContent = "최대 3개까지 선택 가능합니다.";
        styleErrorEl.style.display = "block";
      }

      // 이미 에러 메시지가 떠있다면 클릭 시 숨기기
      if (styleErrorEl.style.display === "block" && selectedStyles.length < 3) {
        styleErrorEl.style.display = "none";
      }
    });

    // 키보드 Tab 이동 시에도 포커스 스타일이 보이도록 tabindex 부여
    btn.setAttribute('tabindex', '0');
  });

  // 3) “선호 카테고리” 버튼 클릭 핸들링
  categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const value = btn.dataset.value;
      const idx   = selectedCategories.indexOf(value);

      if (idx > -1) {
        // 이미 선택 상태 → 해제
        selectedCategories.splice(idx, 1);
        btn.classList.remove('selected');
      } else if (selectedCategories.length < 3) {
        // 최대 3개 미만일 때만 선택
        selectedCategories.push(value);
        btn.classList.add('selected');
      } else {
        // 3개 이미 선택된 상태에서 4번째 클릭 시 에러
        categoryErrorEl.textContent = "최대 3개까지 선택 가능합니다.";
        categoryErrorEl.style.display = "block";
      }

      // 이미 에러 메시지가 떠있다면 클릭 시 숨기기
      if (categoryErrorEl.style.display === "block" && selectedCategories.length < 3) {
        categoryErrorEl.style.display = "none";
      }
    });

    // tabindex 부여 (접근성 및 포커스 가능)
    btn.setAttribute('tabindex', '0');
  });

  // 4) “회원가입 완료” 버튼 클릭 시 검증
  completeBtn.addEventListener('click', e => {
    e.preventDefault();
    let hasError = false;

    // 4-1) 스타일 검증: 최소 1개 선택 여부
    if (selectedStyles.length === 0) {
      styleErrorEl.textContent = "최소 1개 이상의 선호 스타일을 선택해주세요.";
      styleErrorEl.style.display = "block";
      hasError = true;
    } else {
      styleErrorEl.style.display = "none";
    }

    // 4-2) 카테고리 검증: 최소 1개 선택 여부
    if (selectedCategories.length === 0) {
      categoryErrorEl.textContent = "최소 1개 이상의 선호 카테고리를 선택해주세요.";
      categoryErrorEl.style.display = "block";
      hasError = true;
    } else {
      categoryErrorEl.style.display = "none";
    }

    // 4-3) 모두 통과 시 Step 5 이동
    if (!hasError) {
      window.location.href = "/signup/step5/";
    }
  });
}


  // ✅ step5 자리 확보
  else if (path.includes("signup/step5")) {
  const startBtn = document.getElementById('startBtn');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      // 로그인 페이지 URL로 수정
      window.location.href = "/login/";
    });
  }
}
});





