document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const hiddenInput = document.getElementById("hidden-input");
  const boxes = Array.from(document.querySelectorAll(".digit-box"));
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
  const verifBtn = document.querySelector(".verif-comp-btn");
  const errorMsg = document.getElementById("verif-error-msg");

  let timerInterval;
  let remainingTime = 300;

  function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

  function startTimer() {
    errorMsg.style.display = "none";
    hiddenInput.value = "";
    boxes.forEach(box => box.textContent = "");
    clearInterval(timerInterval);
    remainingTime = 300;
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

  startTimer();

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

  logoBtn.addEventListener("click", () => window.location.href = "/login");

  document.querySelector(".digit-boxes").addEventListener("click", () => {
    hiddenInput.focus();
  });

  boxes.forEach(box => {
    box.addEventListener("click", () => hiddenInput.focus());
  });

  hiddenInput.addEventListener("input", (e) => {
    const value = e.target.value.slice(0, 5).replace(/\D/g, "");
    for (let i = 0; i < 5; i++) {
      boxes[i].textContent = value[i] || "";
    }
  });

  hiddenInput.addEventListener("blur", () => {
    setTimeout(() => hiddenInput.focus(), 100);
  });

  hiddenInput.focus();

  verifBtn.addEventListener("click", () => {
    const entered = boxes.map(box => box.textContent).join('');

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
      body: JSON.stringify({ code: entered }),
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = "/pswd_gen";
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
});
