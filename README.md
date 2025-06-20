# SKN09-FINAL-2Team
> SK Networks AI Camp 9기 2팀
> 
> 프로젝트 기간: 25.04.23 - 25.06.20
<br>

#  팀 소개

### 팀명: Senpick

### 팀원 소개
<table>
  <tbody>
   <tr>
    <br>
      <td align=center><b>김우중</b></td>
      <td align=center><b>박주은</b></td>
      <td align=center><b>서예찬</b></td>
      <td align=center><b>유지은</b></td>
       <td align=center><b>허정윤</b></td>
    </tr>
    <tr>
      <td align="center">
          <img alt="Image" src="https://github.com/user-attachments/assets/6388e59a-e07b-4bf0-add1-b02155c4823a" width="200px;" alt="김우중"/>
      <td align="center">
          <img alt="Image" src="https://github.com/user-attachments/assets/4cac2da3-8cbe-41d0-b380-cfe1a1d36792" width="200px;" alt="박주은"/>
      </td>
      <td align="center">
        <img alt="Image" src="https://github.com/user-attachments/assets/4aa26058-5332-480d-83e0-16ae9d5afa44" width="200px;"alt="서예찬" />
      </td>
      <td align="center">
        <img alt="Image" src="https://github.com/user-attachments/assets/c04c8959-5265-4bd4-9c7c-782f0d63d147" width="200px;" alt="유지은"/>
      </td>
       <td align="center">
        <img alt="Image" src="https://github.com/user-attachments/assets/568d6707-31a3-4095-b6bd-8b7fab0b1d36" width="200px;" alt="허정윤"/>
      </td>
      </tr>
    <tr>
      <td><a href="https://github.com/YUJINDL01"><div align=center>@kwj9942</div></a></td>
      <td><a href="https://github.com/syc9811"><div align=center>@pprain1999</div></a></td>
      <td><a href="https://github.com/SIQRIT"><div align=center>@syc9811</div></a></td>
      <td><a href="https://github.com/devunis"><div align=center>@yujitaeng</div></a></td>
      <td><a href="https://github.com/YUJINDL01"><div align=center>@devunis</div></a></td>
    </tr>
  </tbody>
</table>

<br>

# 목차
- [1. 프로젝트 개요](#1-프로젝트-개요)
- [2. WBS](#2-wbs)
- [3. 기술 스택](#3-기술-스택)
- [4. 기능 및 화면 설계](#4-기능-및-화면-설계)
- [5. 데이터 설계](#5-데이터-설계)
- [6. AI추천-시스템-설계](#6-AI추천-시스템-설계)
- [7. 결론](#7-결론)
- [8. 회고](#8-회고)
 

<br>
<br>

# 1. 프로젝트 개요

### 프로젝트 명
**🎁 Senpick** – 감정 기반 AI 선물 추천 서비스

**“마음까지 이해하는 정서형 커머스, Senpick이 선물 선택을 함께합니다.”**

**Senpick** 은 선물 선택이 막막한 순간, 사용자의 감정과 상황을 이해하고 적절한 선물을 추천하여 고민을 줄여주는 **대화형 상품 추천 서비스**입니다.
단순한 필터 기반 추천이 아닌, **LLM 기반 대화 흐름을 통해 맞춤형 상황 정보를 추론하고 공감 기반의 추천**을 제공합니다.

 <br>
 
### 프로젝트 배경
생일, 기념일, 어버이날, 크리스마스, 입학과 승진 등 선물을 해야 하는 순간은 예상보다 훨씬 자주 찾아옵니다.
그러나 부담스럽지 않으면서도 진심이 전해지는 선물을 고르는 일은 쉽지 않아,
매번 고민 끝에 결국 아쉬운 선택에 그치거나, 선물 자체가 스트레스가 되기도 합니다.

대중은 이제 고민 없이 센스 있는 선물을 하고 싶어하며,
이에 따라 추천 시스템의 필요성이 커지고 있습니다.

기업들 역시 이러한 흐름에 맞춰 선물 고민을 덜어줄 AI 추천 서비스 개발에 적극적으로 나서고 있습니다.

<br>

<details>
 <summary>관련 기사</summary>
  
![10명 중 6명 “OO데이는 커뮤니케이션 도구” - 시사타임즈_page-0001](https://github.com/user-attachments/assets/e880d887-75e4-4579-a0dd-f093c8384af7)
  
![파이낸셜뉴스_page-0001](https://github.com/user-attachments/assets/12a3fd04-3e0c-4982-a7d3-2118d1676ead)

![어린이집 보내지도 못하는데…스승의날 선물 고민되는 부모들 _ 연합뉴스_page-0001](https://github.com/user-attachments/assets/d5ad873c-a629-469e-b9dd-ac23fdbe486f)
  </details>


현재 대부분의 추천 시스템은 다음과 같은 한계를 가지고 있습니다.
- 감정이나 관계, 상황 맥락을 제대로 반영하지 못함
- 단순한 조건 필터링에만 의존

→ 이로 인해 사용자 만족도가 낮은 문제가 지속되고 있습니다.

<br>

<details>
<summary> 기존 서비스 분석 </summary>
<p align="center"> <img src="https://github.com/user-attachments/assets/b975715c-e7d0-4217-b708-6df43a59093a" width="600"/><br/> 
  <img src="https://github.com/user-attachments/assets/214ceb47-7fdc-4d3c-bf7c-a2a0dce0c59d" width="600"/> </p>
</details>

저희는 기존 추천 시스템의 한계를 극복하기 위해,
감정과 상황을 이해하는 맞춤형 선물 추천 챗봇 Senpick을 제안합니다.

- 대화형 인터페이스를 통해 사용자의 말투, 맥락, 관계에서 감정 기반 정보 추출
- 파악된 감정과 상황에 어울리는 개인화된 선물을 추천
- 각 추천에 대해 이유를 함께 제시하여 사용자와의 공감을 유도하고 신뢰를 형성
- 빠르고 직관적인 UI/UX를 통해 선물 선택에 드는 고민과 시간 절약
  
→ 이를 통해 **사용자 만족도를 높이고, 고민 없는 선물 선택 경험을 제공**하는 것이 Senpick의 핵심 목표입니다.

<br>

<details>
 <summary>프로젝트 기획서</summary>
 
 ![9기-2팀_프로젝트기획서_page-0001](https://github.com/user-attachments/assets/4996933b-5a97-44b2-836c-8669b3344a90)

 ![9기-2팀_프로젝트기획서_page-0002](https://github.com/user-attachments/assets/e6fad165-e690-4af1-9151-e543bf5ba737)

 ![9기-2팀_프로젝트기획서_page-0003](https://github.com/user-attachments/assets/d133a12c-8314-46b2-8a02-3f96737cba92)


 [프로젝트 기획서 자세히 보기 (PDF)](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%EA%B8%B0%ED%9A%8D%EC%84%9C.pdf)
</details>

<br>

#  2. WBS
<details>
 <summary>WBS</summary>
 
 ![image](https://github.com/user-attachments/assets/5c2b0f10-e901-4541-9090-600982fafccd)
 
</details>
이 프로젝트는 체계적인 SW 개발 프로세스를 기반으로 진행되었으며, 사용자 관점에서 서비스를 개발하고자 하였습니다.
<br><br>

| 문서명 | 설명 | 링크 |
|--------|------|------|
| 프로젝트 기획서 | 서비스의 기획 배경 및 시장 문제 정의 |  [ 바로가기 ](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%EA%B8%B0%ED%9A%8D%EC%84%9C.pdf) |
| 프로젝트 PPT | 전체 프로젝트 설명 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0_2%ED%8C%80_%EC%B5%9C%EC%A2%85PPT.pptx) |
| 요구사항 정의서 | 기능 명세, 비기능 요건 등 포함 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EC%9A%94%EA%B5%AC%EC%82%AC%ED%95%AD%20%EC%A0%95%EC%9D%98%EC%84%9C.pdf)|
| 화면 설계서 | 실제 페이지 흐름과 UI 구조 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%ED%99%94%EB%A9%B4%20%EC%84%A4%EA%B3%84%EC%84%9C.pdf) |
| 데이터베이스 설계서 | 테이블 구조 및 관계도 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%E1%84%80%E1%85%B5-2%E1%84%90%E1%85%B5%E1%86%B7_%E1%84%83%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%90%E1%85%A5%E1%84%87%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%89%E1%85%B3%E1%84%89%E1%85%A5%E1%86%AF%E1%84%80%E1%85%A8%E1%84%89%E1%85%A5.pdf)|
| 모델 테스트 계획 및 결과서 | 주요 기능 테스트 및 성능 평가 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EB%AA%A8%EB%8D%B8%20%ED%85%8C%EC%8A%A4%ED%8A%B8%20%EA%B3%84%ED%9A%8D%20%EB%B0%8F%20%EA%B2%B0%EA%B3%BC%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf) |
| 시스템 테스트 계획 및 결과서 | 주요 기능 테스트 및 성능 평가 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EC%8B%9C%EC%8A%A4%ED%85%9C%20%ED%85%8C%EC%8A%A4%ED%8A%B8%20%EA%B3%84%ED%9A%8D%20%EB%B0%8F%20%EA%B2%B0%EA%B3%BC%EC%84%9C.pdf) |
| 데이터 전처리 결과서 | 수집 및 정제 과정 설명 | [ 바로가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%A0%84%EC%B2%98%EB%A6%AC-%EA%B2%B0%EA%B3%BC%EC%84%9C.pdf) |



<br>
<br>

# 3. 기술 스택
>**개발 환경 및 프로그래밍**
>
>![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)
>![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
>![Jupyter](https://img.shields.io/badge/Jupyter-%23FA0F00.svg?style=for-the-badge&logo=Jupyter&logoColor=white)

>**웹 서비스 및 인프라 구성**
>
>![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white)
>![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=HTML5&logoColor=white)
>![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=black)
>![CSS3](https://img.shields.io/badge/CSS3-264de4?style=for-the-badge&logo=css&logoColor=white)
>![MySQL](https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
>![Amazon RDS](https://img.shields.io/badge/Amazon%20RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white)
>![Amazon S3](https://img.shields.io/badge/Amazon%20S3-232F3E?style=for-the-badge&logo=amazons3&logoColor=white)
>
>![Amazon EC2](https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
>![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white)
>![nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
>![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=Gunicorn&logoColor=white)
>![Amazon AWS](https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)

>**AI 모델 및 프레임워크**
>
>![GPT-4o](https://img.shields.io/badge/GPT--4o-7F27FF?style=for-the-badge&logo=OpenAI&logoColor=white)
>![LangChain](https://img.shields.io/badge/LangChain-005F73?style=for-the-badge&logo=LangChain&logoColor=white)
>![LangGraph](https://img.shields.io/badge/LangGraph-0F4C81?style=for-the-badge&logo=LangChain&logoColor=white)

>**임베딩 및 벡터 검색**
>
>![HuggingFace](https://img.shields.io/badge/HuggingFace-multilingual--e5--large--instruct-blue?logo=huggingface)
>![Qdrant](https://img.shields.io/badge/Qdrant-8084b7?style=for-the-badge&logo=Qdrant&logoColor=white)

>**협업 및 형상관리**
>
>![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
>![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)

<br>

##  시스템 구성도

![시스템 아키텍처](docs/9기-2팀_시스템아키텍쳐%20FINAL.drawio.png)

<br>
<br>



# 4. 기능 및 화면 설계

## 요구 사항

- 6개의 업무 구분과 20개의 요구사항 ID를 정의


![image](https://github.com/user-attachments/assets/18f990bc-725b-4b0d-b7a9-08beef29ef35)

<details>

<summary>요구사항 정의서</summary>

![9기-2팀_요구사항 정의서-이미지-0](https://github.com/user-attachments/assets/a139f032-1415-4b36-9c6e-7dbf8d9bcaee)


![9기-2팀_요구사항 정의서-이미지-1](https://github.com/user-attachments/assets/f22abc69-620b-4851-a777-b41d96996e51)
</details>

<br>

## UI/UX 설계

![image](https://github.com/user-attachments/assets/b8db9918-0844-4dce-a760-d09e2b0296c8)


![image](https://github.com/user-attachments/assets/73510db0-5a1d-426d-96bd-433d13c74f4b)

![image](https://github.com/user-attachments/assets/801e08ae-e30e-4c45-8dc0-0c6ef713a12b)



<details>
 <summary>시나리오 설계서 </summary>
 
![9기-2팀_시나리오 설계서_page-0001](https://github.com/user-attachments/assets/c2b4f42d-6da5-46f1-886d-23dc60d2cb08)

![9기-2팀_시나리오 설계서_page-0002](https://github.com/user-attachments/assets/0e650787-510e-4f35-84a7-340f006965a4)

![9기-2팀_시나리오 설계서_page-0003](https://github.com/user-attachments/assets/bbaaf75c-836b-4173-a059-85b646fd26d5)

[시나리오 설계서 자세히 보러가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EC%8B%9C%EB%82%98%EB%A6%AC%EC%98%A4%20%EC%84%A4%EA%B3%84%EC%84%9C.pdf)

</details>

<details>
 <summary>화면 설계서 </summary>
  
![9기-2팀_화면 설계서_page-0002](https://github.com/user-attachments/assets/6f5ace46-6fb7-4e02-a19a-2360696d8e4e)

![9기-2팀_화면 설계서_page-0016](https://github.com/user-attachments/assets/4165b1bf-2f79-45e3-9b17-ec6f8582d6ee)

![9기-2팀_화면 설계서_page-0017](https://github.com/user-attachments/assets/2a9cf1f9-6e69-4110-a68d-e568e21da911)

![9기-2팀_화면 설계서_page-0019](https://github.com/user-attachments/assets/3b485886-82c3-47fa-b5d8-8f8743afae70)

![9기-2팀_화면 설계서_page-0020](https://github.com/user-attachments/assets/a6cf7b77-dcd6-4caf-bc9e-325d9f3eadfa)



[화면설계서 자세히 보러가기 ](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%ED%99%94%EB%A9%B4%20%EC%84%A4%EA%B3%84%EC%84%9C.pdf)

</details>

<br>
<br>

# 5. 데이터 설계
![image](https://github.com/user-attachments/assets/5d0d1a9d-69e6-4bbb-af3d-877fa8ab1c22)

**[ERD]**

![image](https://github.com/user-attachments/assets/3db1089e-9b66-48da-9db0-ac1d02221eaa)


<details>
 <summary>데이터 전처리 결과서 </summary>
 
  ![9기-2팀_데이터전처리-결과서_page-0001](https://github.com/user-attachments/assets/a69f22f0-63e2-462a-ae77-0c7d0621eb2a)
 
  ![9기-2팀_데이터전처리-결과서_page-0002](https://github.com/user-attachments/assets/4f9706f4-3225-4d79-ad11-3401c0d66619)
  
  ![9기-2팀_데이터전처리-결과서_page-0003](https://github.com/user-attachments/assets/0de22ee8-1eb5-45cc-9126-2edd51d5cb33)



[데이터 전처리 결과서 자세히 보러가기 ](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%A0%84%EC%B2%98%EB%A6%AC-%EA%B2%B0%EA%B3%BC%EC%84%9C.pdf)

</details>

<br>
<br>

#  6. AI/추천 시스템 설계

- 사용 모델: OpenAI GPT-4 + 사용자 시나리오 기반 Prompt 설계
  
![image](https://github.com/user-attachments/assets/f38d0a2b-26b8-494d-92d1-a5a6dfdc6a36)

**[모델 구조]**

![image](https://github.com/user-attachments/assets/539cc254-3f4b-4c52-b7c0-1e8114f6bc0f)



<details>
 <summary>모델 테스트 계획 및 결과보고서 </summary> 

### <테스트 계획>
   
![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0001](https://github.com/user-attachments/assets/c05cb468-e338-478f-b98a-a61128bd611b)
  
![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0002](https://github.com/user-attachments/assets/8c67cb6d-8758-4577-a82e-64c4f7c978d1)

![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0003](https://github.com/user-attachments/assets/e5ffaf14-6440-4354-a32f-edea5be3bc84)

<br>
   
### <테스트 결과>
 ![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0008](https://github.com/user-attachments/assets/88892af8-a4c1-4a91-83fa-f98e31f7bd61)
![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0009](https://github.com/user-attachments/assets/8760f02a-3fc5-491c-b8b0-83f34b8ec9e2)


[테스트 계획 및 결과 보고서 자세히 보러가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EB%AA%A8%EB%8D%B8%20%ED%85%8C%EC%8A%A4%ED%8A%B8%20%EA%B3%84%ED%9A%8D%20%EB%B0%8F%20%EA%B2%B0%EA%B3%BC%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf)

</details>

**[Agent 구조]**

![image](https://github.com/user-attachments/assets/d2c21802-e0f6-426e-80a8-d28846c6574d)

![image](https://github.com/user-attachments/assets/c37e073e-6275-4332-941b-d4fb289872da)


<br>

<details>
 <summary>AI 학습 결과서</summary>
 

 ![9기-2팀_인공지능 학습 결과서_page-0001](https://github.com/user-attachments/assets/83970e3d-2f81-4c2c-931e-9163d5f7729a)

![9기-2팀_인공지능 학습 결과서_page-0002](https://github.com/user-attachments/assets/15324d7b-57f6-4196-bc39-6ef017060940)

![9기-2팀_인공지능 학습 결과서_page-0003](https://github.com/user-attachments/assets/29977c9d-cfff-440f-9f84-d849d9234b3c)

![9기-2팀_인공지능 학습 결과서_page-0004](https://github.com/user-attachments/assets/841a565d-95f5-45cd-94ec-fd04dd5f7820)

 [AI 학습 결과서 자세히 보기 ](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5%20%ED%95%99%EC%8A%B5%20%EA%B2%B0%EA%B3%BC%EC%84%9C.pdf)
</details>

<details>
 <summary>테스트 계획 및 결과보고서 </summary> 

### <테스트 계획>

![9기-2팀_시스템 테스트 계획 및 결과서_page-0001](https://github.com/user-attachments/assets/4b23df85-425c-41e3-8e7a-6db68db0fe90)


<br>
   
### <테스트 결과>

![9기-2팀_시스템 테스트 계획 및 결과서_page-0003](https://github.com/user-attachments/assets/f7eeb14e-a810-493e-8f57-87c8040fe770)

![9기-2팀_시스템 테스트 계획 및 결과서_page-0004](https://github.com/user-attachments/assets/ffa38123-df94-4e30-bad8-53466a2161fc)

![9기-2팀_시스템 테스트 계획 및 결과서_page-0005](https://github.com/user-attachments/assets/f42d9fac-0101-4eaf-b32f-17d1fcb7b270)

[시스템 테스트 계획 및 결과 보고서 자세히 보러가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EC%8B%9C%EC%8A%A4%ED%85%9C%20%ED%85%8C%EC%8A%A4%ED%8A%B8%20%EA%B3%84%ED%9A%8D%20%EB%B0%8F%20%EA%B2%B0%EA%B3%BC%EC%84%9C.pdf)

</details>

<br>
<br>

#  7. 결론

## 시연 영상

**[메인 플로우]**  
- 로그인 > 수령인 정보 입력 > 센픽과 대화 > 상품 추천 > 다른 추천 받기

![2팀 최종 시연 영상 (1) (1)](https://github.com/user-attachments/assets/27f1861e-7eab-4608-8385-e5f5ddfd7e98)

![2팀 최종 시연 영상 (1) (2)](https://github.com/user-attachments/assets/ab87d282-e48a-4d6f-9028-4c55f4621a0f)


<br>

**[상품 비교 플로우]**
- 여러개의 상품 추천 속에서 특정 **상품 2개를 골라 비교** 요구
- **추천 히스토리 사이드바**를 통해 추천 상품 확인 및 비교 가능
- 마이페이지 내 **채팅별 좋아요 히스토리**를 통해 채팅별 상품 및 이력 확인 가능

![2팀 최종 시연 영상 (1) (3)](https://github.com/user-attachments/assets/5db8af20-60b3-443f-927f-a4c2af668266)

![2팀 최종 시연 영상 (1) (4)](https://github.com/user-attachments/assets/dfe86078-a1af-4e2a-8fe6-26fd5a4a996e)

<br>

**[생일 축하 플로우]**
- **생일인 사용자 전용 축하 인터페이스**
- 대화 속, 축하 메세지
- 생일 축하 전용 메뉴 생성
- 사용자가 **셀프 선물** 할 수 있도록 사용자에게 맞춰진 선물 추천

![2팀 최종 시연 영상 (1) (5)](https://github.com/user-attachments/assets/2dd41af5-4164-4bf9-b139-0f5c2e9f71b1)


<br>

## 결과 및 사용자 피드백
[사용자 테스트 설문 결과]

![image](https://github.com/user-attachments/assets/1888b47e-33e8-48c1-a84a-3b2f708cdbe0)

[평가]

![image](https://github.com/user-attachments/assets/a1bc90e7-c62d-46ae-aea3-fbeae3387abf)

[기대 효과]

![image](https://github.com/user-attachments/assets/878c4c7c-bde9-4f78-827c-471d7728ce60)

[확장 가능성]

![image](https://github.com/user-attachments/assets/c9991fa9-9c44-4a3d-98bf-426c42705560)


<br>
<br>

# 8. 회고
- 🤓김우중:이번 프로젝트를 통해 사용자 정보 수집부터 AI 기반 추천까지 전반적인 서비스 흐름을 직접 구현하며 큰 성장을 느꼈습니다. 특히 소셜 로그인 후 불완전한 사용자 정보를 단계적으로 수집하는 로직 설계가 어려웠지만, 조건 분기와 리디렉션 구조를 정교하게 조정해 문제를 해결할 수 있었습니다. 전체적으로 사용자 경험을 중심에 둔 개발의 중요성을 다시 한번 체감 했습니다.
- 🙂박주은:
- 🫡서예찬: 초기에는 LangChain의 ReAct 기반 구조만으로 선물 추천을 구현했지만, 조건이 충분하지 않아도 추천이 이뤄지는 문제가 있었습니다. 이를 해결하기 위해 LangGraph 기반 FSM 구조로 재설계하고, 상황 정보가 모두 충족된 경우에만 agent를 실행하도록 흐름을 통제했습니다. 그 결과 추천 정확도와 사용자 만족도가 향상되었고, 프론트와 백엔드 간 조건 판단 기준도 일관되게 유지할 수 있었습니다. 이 과정을 통해 단순한 agent 호출만으로는 복잡한 대화 흐름을 제어하기 어렵다는 점을 체감했고, FSM 기반 제어의 중요성과 안정성을 직접 경험할 수 있었습니다.
- 😜유지은: 이번 프로젝트는 감정과 관계 같은 비정형 정보를 기반으로 한 정서형 선물 추천 서비스로, 기획 초기부터 구조화된 데이터 설계와 프론트–백엔드–모델 간의 유기적 연결이 중요했습니다. 진행 과정에서 추천 결과와 사용자 맥락 간 불일치 문제가 발생해, 이를 해결하기 위해 프롬프트를 상황별로 세분화하고 Top-k 값을 조정해 추천 정확도를 높였습니다. 그 결과, 추천의 맥락 일치도가 향상되었고, 기획과 기술을 연결하는 문제 해결 역량을 강화할 수 있었습니다. 시장성 있는 서비스 개발을 기획부터 설계, 개발을 하고 테스트를 할 수 있었던 값진 경험이었습니다.
- 😆허정윤: 이번 프로젝트 SenPick은 GPT API 단일 모델에 프롬프트를 적용하는 방식에서 벗어나, LangChain과 LangGraph를 활용해 각 기능에 특화된 프롬프트를 설계하고 조합함으로써 복합적인 추천 서비스를 구현한 경험이었습니다. 대화를 진행하는 모델, 상황을 추출하는 모델, 추천을 수행하는 모델, 사용자의 의도를 파악하는 모델 등 여러 역할을 분리해 구성한 점이 특히 인상 깊었습니다. 각기 다른 모델이 협력해 하나의 결과를 만들어내는 과정이 신기했고, 단순한 챗봇을 넘어 더 정교한 AI 시스템을 만들어본 특별한 경험이었습니다.
