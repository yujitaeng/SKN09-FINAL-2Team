document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const verifyConfirmBtn = document.querySelector(".verif-comp-btn"); // 인증 완료 버튼
  const resendText = document.getElementById("resend-text");
  const timerText = document.getElementById("timer-text");
  const errorMsg = document.getElementById("verif-error-msg");
  const inputs = document.querySelectorAll('.verify-input');

  let timerInterval;
  let remainingTime = 300;

  // 쿠키 가져오기
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }

  // 타이머 시작
  function startTimer() {
    errorMsg.style.display = "none";
    inputs.forEach(input => input.value = ""); // 입력 초기화

    clearInterval(timerInterval);
    remainingTime = 300;
    updateTimer();
    timerText.style.display = "block";

    timerInterval = setInterval(() => {
      remainingTime--;
      if (remainingTime >= 0) {
        updateTimer();
      }
      if (remainingTime === 0) {
        clearInterval(timerInterval);
      }
    }, 1000);
  }

  // 타이머 텍스트 업데이트
  function updateTimer() {
    const minutes = String(Math.floor(remainingTime / 60)).padStart(2, '0');
    const seconds = String(remainingTime % 60).padStart(2, '0');
    timerText.textContent = `${minutes}:${seconds}`;
  }

  // 인증번호 입력 제어
  inputs.forEach((input, idx) => {
    input.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, '');
      if (e.target.value.length > 1) {
        e.target.value = e.target.value.slice(0, 1);
      }
      // 다음 칸으로 이동
      if (e.target.value && idx < inputs.length - 1) {
        inputs[idx + 1].focus();
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !e.target.value && idx > 0) {
        inputs[idx - 1].focus();
      }
    });
  });

  // 인증번호 확인 요청
  verifyConfirmBtn.addEventListener('click', () => {
    const code = Array.from(inputs).map(input => input.value).join('');
    console.log(code); // 확인용

    if (remainingTime <= 0) {
      errorMsg.textContent = "인증 시간이 만료되었습니다. 인증번호 재전송 요청 후 재입력 부탁드립니다.";
      errorMsg.style.display = "block";
      return;
    }

    fetch("/api/verify_code/", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({ code }),
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = "/pswd/gen"; // 주소 수정 주의
      } else {
        errorMsg.textContent = data.message || "인증번호가 올바르지 않습니다.";
        errorMsg.style.display = "block";
      }
    })
    .catch(() => {
      errorMsg.textContent = "서버 통신 오류. 다시 시도해 주세요.";
      errorMsg.style.display = "block";
    });
  });

  // 인증번호 재전송 요청
  resendText.addEventListener("click", () => {
    fetch("/api/resend_code/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        startTimer();
      } else {
        errorMsg.textContent = data.message || "인증번호 재전송 실패";
        errorMsg.style.display = "block";
      }
    });
  });

  // 로고 클릭 시 로그인 이동
  logoBtn.addEventListener("click", () => window.location.href = "/login");

  // 초기 포커스
  if (inputs.length > 0) {
    inputs[0].focus();
  }

  // 타이머 시작
  startTimer();
  resendText.click(); // 초기 인증번호 재전송 요청
});
