document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const testButton = document.querySelector(".pswd-verif-test");

  const hiddenInput = document.getElementById("hidden-input");
  const boxes = Array.from(document.querySelectorAll(".digit-box"));

  const timerText = document.getElementById("timer-text");
  const resendText = document.getElementById("resend-text");
  const verifBtn = document.querySelector(".verif-comp-btn"); // 인증완료 버튼

  let timerInterval;
  let remainingTime = 5*60; // 5분 (현재는 테스트용 3초)

  // function startTimer() {
  //   document.getElementById("verif-error-msg").style.display = "none";
  //   clearInterval(timerInterval);
  //   remainingTime = 3;
  //   updateTimer();
  //   timerText.style.display = "block";
  //   resendText.style.display = "none";

  //   timerInterval = setInterval(() => {
  //     remainingTime--;
  //     if (remainingTime >= 0) {
  //       updateTimer();
  //     }
  //     if (remainingTime === 0) {
  //       clearInterval(timerInterval);
  //       resendText.style.display = "block";
  //     }
  //   }, 1000);
  // }
  function startTimer() {
    // 🔹 오류 메시지 숨기기
    document.getElementById("verif-error-msg").style.display = "none";

    // 🔹 입력 초기화
    hiddenInput.value = ""; // 실제 입력 값 초기화
    boxes.forEach(box => box.textContent = ""); // 각 digit-box 시각적 숫자 초기화

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
  logoBtn.addEventListener("click", () => window.location.href = "/login");

  // // 테스트용 버튼 → 강제 이동
  // testButton.addEventListener("click", function () {
  //   window.location.href = "/pswd_gen";
  // });

  // 클릭 시 입력 포커스
  document.querySelector(".digit-boxes").addEventListener("click", () => {
    hiddenInput.focus();
  });

  boxes.forEach(box => {
    box.addEventListener("click", () => hiddenInput.focus());
  });

  hiddenInput.addEventListener("input", (e) => {
    const value = e.target.value.slice(0, 5).replace(/\D/g, "");
    console.log("입력된 값:", value);  // ✅ 확인용 로그
    for (let i = 0; i < 5; i++) {
      boxes[i].textContent = value[i] || "";
    }
  });

  hiddenInput.addEventListener("blur", () => {
    setTimeout(() => hiddenInput.focus(), 100);
  });

  hiddenInput.focus();

  // 이메일 인증 완료 버튼 → 입력값 체크 후 이동
  verifBtn.addEventListener("click", () => {
    const entered = boxes.map(box => box.textContent).join('');
    const testCode = "12345";
    const errorMsg = document.getElementById("verif-error-msg");

    if (remainingTime <= 0) {
      errorMsg.textContent = "인증 시간이 만료되었습니다. 인증번호 재전송 요청 후 재입력 부탁드립니다.";
      errorMsg.style.display = "block";
      return;
    }

    if (entered !== testCode) {
      errorMsg.textContent = "인증번호가 올바르지 않습니다.";
      errorMsg.style.display = "block";
      return;
    }

    // 인증 성공
    window.location.href = "/pswd_gen";
  });


});
