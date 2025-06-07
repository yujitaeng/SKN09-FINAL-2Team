document.addEventListener("DOMContentLoaded", function () {
  const logoBtn = document.querySelector(".logo");
  const hiddenInput = document.getElementById("hidden-input");
  const boxes = Array.from(document.querySelectorAll(".digit-box"));
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
