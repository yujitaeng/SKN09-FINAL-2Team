document.addEventListener("DOMContentLoaded", function () {
  // 슬라이드 기능 초기화
  // 3) 인증번호 입력박스(5칸) 제어: 숫자만 허용 + 다음칸 자동 포커스
  const inputs = document.querySelectorAll('.verify-input');
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
  
  const verifyConfirmBtn = document.querySelector('.verif-comp-btn'); // 인증 완료 버튼
  verifyConfirmBtn.addEventListener('click', function() {
    const inputs = document.querySelectorAll('.verify-input');   // 5칸 입력박스
    const code = Array.from(inputs).map(input => input.value).join('');
    console.log(code); // 입력된 값 확인용
    
    const testCode = "12345";
    const errorMsg = document.getElementById("verif-error-msg");

    if (remainingTime <= 0) {
      errorMsg.textContent = "인증 시간이 만료되었습니다. 인증번호 재전송 요청 후 재입력 부탁드립니다.";
      errorMsg.style.display = "block";
      return;
    }

    if (code !== testCode) {
      errorMsg.textContent = "인증번호가 올바르지 않습니다.";
      errorMsg.style.display = "block";
      return;
    }

    // 인증 성공
    window.location.href = "/pswd/gen";
  });

  const timerText = document.getElementById("timer-text");
  const resendText = document.getElementById("resend-text");
  const verifBtn = document.querySelector(".verif-comp-btn"); // 인증완료 버튼

  let timerInterval;
  let remainingTime = 5*60; // 5분 (현재는 테스트용 3초)

  function startTimer() {
    // 🔹 오류 메시지 숨기기
    document.getElementById("verif-error-msg").style.display = "none";

    // 🔹 타이머 초기화
    clearInterval(timerInterval);
    remainingTime = 5*60;
    updateTimer();
    timerText.style.display = "block";
    resendText.style.display = "none";

    timerInterval = setInterval(() => {
      remainingTime--;
      if (remainingTime >= 0) {
        updateTimer();
      }
      if (remainingTime === 0) {
        clearInterval(timerInterval);
        resendText.style.display = "block";
      }
    }, 1000);
  }


  function updateTimer() {
    const minutes = String(Math.floor(remainingTime / 60)).padStart(2, '0');
    const seconds = String(remainingTime % 60).padStart(2, '0');
    timerText.textContent = `${minutes}:${seconds}`;
  }

  // 초기 타이머 시작
  startTimer();

  // 인증코드 재전송 클릭
  resendText.addEventListener("click", startTimer);

  // 로고 클릭
  const logoBtn = document.querySelector(".logo");
  logoBtn.addEventListener("click", () => window.location.href = "/login");
});
