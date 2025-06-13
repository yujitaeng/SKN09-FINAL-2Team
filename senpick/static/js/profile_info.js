document.addEventListener("DOMContentLoaded", function () {
  // ------------------------ 성별 선택 ------------------------
  document.querySelectorAll(".gender-toggle .gender").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".gender-toggle .gender").forEach((el) =>
        el.classList.remove("active")
      );
      btn.classList.add("active");
    });
  });

  // ------------------------ 드롭다운 직업 선택 ------------------------
  const jobInput = document.querySelector(".job-input input");
  const jobDropdown = document.createElement("ul");
  jobDropdown.className = "job-dropdown";
  const jobList = [
    "학생/취준생", "직장인", "전문직", "창작/문화 종사자", "공공/공무 종사자",
    "자영업자", "주부", "비직업군", "기타"
  ];

  jobList.forEach((job) => {
    const li = document.createElement("li");
    li.textContent = job;
    li.addEventListener("click", (e) => {
      e.stopPropagation();
      jobInput.value = job;
      jobDropdown.style.display = "none";
      validateJob();
    });
    jobDropdown.appendChild(li);
  });

  document.querySelector(".job-input").appendChild(jobDropdown);

  jobInput.parentNode.addEventListener("click", (e) => {
    e.stopPropagation(); // Prevent click from closing the dropdown
    jobDropdown.style.display = "block";
  });

  jobInput.addEventListener("focus", () => {
    jobDropdown.style.display = "block";
  });

  document.addEventListener("click", (e) => {
    if (!document.querySelector(".job-input").contains(e.target)) {
      jobDropdown.style.display = "none";
    }
  });

  // ------------------------ 선택 최대 3개 ------------------------
  handleTagLimit(".preference-tags:nth-of-type(1) .tag", 3);
  handleTagLimit(".preference-tags:nth-of-type(2) .tag", 3);

  function handleTagLimit(selector, maxCount) {
    const tags = document.querySelectorAll(selector);
    tags.forEach((tag) => {
      tag.addEventListener("click", () => {
        const container = tag.closest(".preference-tags");
        const isStyle = container.classList.contains("style-tags");
        const isCategory = container.classList.contains("category-tags");

        if (tag.classList.contains("active")) {
          tag.classList.remove("active");
        } else {
          const activeCount = Array.from(tags).filter((t) =>
            t.classList.contains("active")
          ).length;
          if (activeCount < maxCount) {
            tag.classList.add("active");
          } else {
            alert(`최대 ${maxCount}개까지만 선택할 수 있습니다.`);
          }
        }

        if (isStyle) validateStyleTags();
        if (isCategory) validateCategoryTags();
      });
    });
  }

  // ------------------------ 유효성 검사 ------------------------
  const form = document.querySelector("form");
  const password = form.querySelector("#password");
  const nickname = form.querySelector("#nickname");
  const birth = form.querySelector("#birth");

  form.addEventListener("submit", function (e) {
    let isValid = true;

    const genderSelected = document.querySelector(".gender-toggle .active");
    const selectedStyleTags = document.querySelectorAll(".style-tags .tag.active");
    const selectedCategoryTags = document.querySelectorAll(".category-tags .tag.active");

    clearError(password);
    clearError(nickname);
    clearError(birth);
    clearError(jobInput);

    const pwRegex = /^(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$^*()_\+\-=\[\]{}])[a-z0-9!@#$^*()_\+\-=\[\]{}]{8,15}$/;

    if (!password.value || !pwRegex.test(password.value)) {
      setError(password, "비밀번호를 입력해주세요. *영문 소문자, 숫자, 특수문자(!@#$^*()_+-=[]{})를 포함하여 8~15자");
      alert("비밀번호를 입력해주세요. *영문 소문자, 숫자, 특수문자(!@#$^*()_+-=[]{})를 포함하여 8~15자");
      isValid = false;
    }

    if (!nickname.value) {
      setError(nickname, "닉네임을 입력해주세요. *한글 2~8자");
      isValid = false;
    } else if (!/^[가-힣]{2,8}$/.test(nickname.value)) {
      setError(nickname, "닉네임은 한글 2~8자로 입력해주세요.");
      isValid = false;
    }

    if (!birth.value || !/^[0-9]{8}$/.test(birth.value)) {
      setError(birth, "생년월일이 올바르지 않습니다. (숫자만 8자리 입력)");
      isValid = false;
    }

    if (!genderSelected) {
      alert("성별을 선택해주세요.");
      isValid = false;
    }

    if (!jobInput.value || jobInput.value.trim() === "") {
      setError(jobInput, "직업을 선택해주세요.");
      isValid = false;
    }

    if (selectedStyleTags.length < 1) {
      alert("선호 스타일을 선택해주세요. 최대 3개 선택 가능.");
      isValid = false;
    }

    if (selectedCategoryTags.length < 1) {
      alert("선호 카테고리를 선택해주세요. 최대 3개 선택 가능.");
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault(); // Prevent form submission if validation fails
    }
  });

  // ------------------------ 실시간 유효성 검사 ------------------------
  function validatePassword() {
    if (!password.value || password.value.length < 8 || password.value.length > 15) {
      setError(password, "비밀번호를 입력해 주세요.");
    } else {
      clearError(password);
    }
  }
  password.addEventListener("input", validatePassword);
  password.addEventListener("focus", validatePassword);

  function validateNickname() {
    if (!nickname.value) {
      setError(nickname, "닉네임을 입력해주세요. *한글 2~8자");
    } else if (!/^[가-힣]{2,8}$/.test(nickname.value)) {
      setError(nickname, "닉네임은 한글 2~8자로 입력해주세요.");
    } else {
      clearError(nickname);
    }
  }
  nickname.addEventListener("input", validateNickname);
  nickname.addEventListener("focus", validateNickname);

  function validateBirth() {
    if (!/^[0-9]{8}$/.test(birth.value)) {
      setError(birth, "생년월일이 올바르지 않습니다. (숫자만 8자리 입력)");
    } else {
      clearError(birth);
    }
  }
  birth.addEventListener("input", validateBirth);
  birth.addEventListener("focus", validateBirth);

  function validateJob() {
    if (!jobInput.value || jobInput.value.trim() === "") {
      setError(jobInput, "직업을 선택해주세요.");
    } else {
      clearError(jobInput);
    }
  }
  jobInput.addEventListener("input", validateJob);
  jobInput.addEventListener("focus", validateJob);

  function validateStyleTags() {
    const selected = document.querySelectorAll(".style-tags .tag.active");
    if (selected.length < 3) {
      setError(document.querySelector(".style-tags"), "선호 스타일을 선택해주세요. 최대 3개 선택 가능.");
    } else {
      clearError(document.querySelector(".style-tags"));
    }
  }

  function validateCategoryTags() {
    const selected = document.querySelectorAll(".category-tags .tag.active");
    if (selected.length < 3) {
      setError(document.querySelector(".category-tags"), "선호 카테고리를 선택해주세요. 최대 3개 선택 가능.");
    } else {
      clearError(document.querySelector(".category-tags"));
    }
  }

  // ------------------------ 헬퍼 함수 ------------------------
  function setError(el, message) {
    el.classList.add("error");
    if (el.nextElementSibling && el.nextElementSibling.classList.contains("error-message")) {
      el.nextElementSibling.textContent = message;
    } else {
      let msg = document.createElement("p");
      msg.className = "error-message";
      msg.style.color = "#EB1C24";
      msg.style.fontSize = "13px";
      msg.style.marginTop = "6px";
      msg.textContent = message;
      el.insertAdjacentElement("afterend", msg);
    }
  }

  function clearError(el) {
    el.classList.remove("error");
    if (el.nextElementSibling && el.nextElementSibling.classList.contains("error-message")) {
      el.nextElementSibling.remove();
    }
  }
});
