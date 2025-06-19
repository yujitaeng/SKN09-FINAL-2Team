# SKN09-FINAL-2Team
> SK Networks AI Camp 9기 2팀
> 
> 프로젝트 기간: 25.04.23 - 25.06.20
<br>

#  팀 소개
>
>### 팀명: Senpick
>>### 팀원 소개
><table align=center>
>  <tbody>
>   <tr>
>    <br>
>      <td align=center><b>김우중</b></td>
>      <td align=center><b>박주은</b></td>
>      <td align=center><b>서예찬</b></td>
>      <td align=center><b>유지은</b></td>
>       <td align=center><b>허정윤</b></td>
>    </tr>
>    
>    <tr>
>      <td><a href="https://github.com/YUJINDL01"><div align=center>@kwj9942</div></a></td>
>      <td><a href="https://github.com/syc9811"><div align=center>@pprain1999</div></a></td>
>      <td><a href="https://github.com/SIQRIT"><div align=center>@syc9811</div></a></td>
>      <td><a href="https://github.com/devunis"><div align=center>@yujitaeng</div></a></td>
>      <td><a href="https://github.com/YUJINDL01"><div align=center>@devunis</div></a></td>
>    </tr>
>  </tbody>
></table>
><br>
>
# 프로젝트 개요

>### 프로젝트 명
>- **Senpick**:LLM기반 상품 추천 서비스
>> **Senpick** 은 선물 선택이 막막한 순간, 사용자의 감정과 상황을 이해하고 적절한 선물을 추천하여 고민을 줄여주는 **대화형 상품 추천 서비스**입니다.
>> 단순한 필터 기반 추천이 아닌, **LLM 기반 대화 흐름을 통해 맞춤형 상황 정보를 추론하고 공감 기반의 추천**을 제공합니다.
>> 
>### 프로젝트 배경
>생일, 기념일, 어버이날, 크리스마스, 입학과 승진 등 선물을 해야 하는 순간은 예상보다 훨씬 자주 찾아옵니다.
>그러나 부담스럽지 않으면서도 진심이 전해지는 선물을 고르는 일은 쉽지 않아,
>매번 고민 끝에 결국 아쉬운 선택에 그치거나, 선물 자체가 스트레스가 되기도 합니다.
>
>대중은 이제 고민 없이 센스 있는 선물을 하고 싶어하며,
>이에 따라 추천 시스템의 필요성이 커지고 있습니다.
>
>기업들 역시 이러한 흐름에 맞춰 선물 고민을 덜어줄 AI 추천 서비스 개발에 적극적으로 나서고 있습니다.
>
<details>
 <summary>관련 기사</summary>
  
![10명 중 6명 “OO데이는 커뮤니케이션 도구” - 시사타임즈_page-0001](https://github.com/user-attachments/assets/e880d887-75e4-4579-a0dd-f093c8384af7)
  
![파이낸셜뉴스_page-0001](https://github.com/user-attachments/assets/12a3fd04-3e0c-4982-a7d3-2118d1676ead)

![어린이집 보내지도 못하는데…스승의날 선물 고민되는 부모들 _ 연합뉴스_page-0001](https://github.com/user-attachments/assets/d5ad873c-a629-469e-b9dd-ac23fdbe486f)
  </details>


>현재 대부분의 추천 시스템은 다음과 같은 한계를 가지고 있습니다:
>
>감정이나 관계, 상황 맥락을 제대로 반영하지 못함
>
>단순한 조건 필터링에만 의존
>
>→ 이로 인해 사용자 만족도가 낮은 문제가 지속되고 있습니다.
>
<details>
<summary> 시장조사 </summary>
<p align="center"> <img src="https://github.com/user-attachments/assets/b975715c-e7d0-4217-b708-6df43a59093a" width="600"/><br/> 
  <img src="https://github.com/user-attachments/assets/214ceb47-7fdc-4d3c-bf7c-a2a0dce0c59d" width="600"/> </p>
</details>

>저희는 기존 추천 시스템의 한계를 극복하기 위해,
>감정과 상황을 이해하는 맞춤형 선물 추천 챗봇 Senpick을 제안합니다.
>
>- 대화형 인터페이스를 통해 사용자의 말투, 맥락, 관계에서 감정 기반 정보를 추출합니다.
>
>- 파악된 감정과 상황에 어울리는 개인화된 선물을 추천합니다.
>
>- 각 추천에 대해 이유를 함께 제시하여 사용자와의 공감을 유도하고 신뢰를 형성합니다.
>
>- 빠르고 직관적인 UI/UX를 통해 선물 선택에 드는 고민과 시간을 줄여줍니다.
>
>→ 이를 통해 사용자 만족도를 높이고,
>고민 없는 선물 선택 경험을 제공하는 것이 Senpick의 핵심 목표입니다.







# 2. 기술 스택
| 분야                   | 기술 및 라이브러리 |
|------------------------|------------------|
| **프로그래밍 언어 & 개발환경** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=black) ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-%23FA0F00.svg?style=for-the-badge&logo=Jupyter&logoColor=white) 
| **웹 프레임워크** | ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=HTML5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-663399?style=for-the-badge&logo=css3&logoColor=white)
| **워크플로우 설계** | ![LangChain](https://img.shields.io/badge/LangChain-005F73?style=for-the-badge&logo=LangChain&logoColor=white) ![LangGraph](https://img.shields.io/badge/LangGraph-0F4C81?style=for-the-badge&logo=LangChain&logoColor=white) |
| **AI 모델** | ![GPT-4o](https://img.shields.io/badge/GPT--4o-7F27FF?style=for-the-badge&logo=OpenAI&logoColor=white) |
| **데이터베이스 및 임베딩** | ![Qdrant](https://img.shields.io/badge/Qdrant-16B1B1?style=for-the-badge&logo=Qdrant&logoColor=white) |
| **서버** | ![nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=Gunicorn&logoColor=white) |
| **인프라 및 배포** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white) ![Amazon AWS](https://img.shields.io/badge/Amazon%20AWS-232F3E?style=for-the-badge&logo=Amazon%20AWS&logoColor=white) |
| **협업 및 형상관리** | ![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=Discord&logoColor=white) ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white) |
#  시스템 구성도

![시스템 아키텍처](docs/9기-2팀_시스템아키텍쳐%20FINAL.drawio.png)
# 요구사항 정의서
<details>
 


![9기-2팀_요구사항 정의서-이미지-0](https://github.com/user-attachments/assets/a139f032-1415-4b36-9c6e-7dbf8d9bcaee)


![9기-2팀_요구사항 정의서-이미지-1](https://github.com/user-attachments/assets/f22abc69-620b-4851-a777-b41d96996e51)
</details>

#  화면설계서
<details>
 <summary>화면 설계서 </summary>
  
![9기-2팀_화면 설계서_page-0002](https://github.com/user-attachments/assets/6f5ace46-6fb7-4e02-a19a-2360696d8e4e)

![9기-2팀_화면 설계서_page-0016](https://github.com/user-attachments/assets/4165b1bf-2f79-45e3-9b17-ec6f8582d6ee)

![9기-2팀_화면 설계서_page-0017](https://github.com/user-attachments/assets/2a9cf1f9-6e69-4110-a68d-e568e21da911)

![9기-2팀_화면 설계서_page-0019](https://github.com/user-attachments/assets/3b485886-82c3-47fa-b5d8-8f8743afae70)

![9기-2팀_화면 설계서_page-0020](https://github.com/user-attachments/assets/a6cf7b77-dcd6-4caf-bc9e-325d9f3eadfa)

</details>


[화면설계서 자세히 보러가기 ](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%ED%99%94%EB%A9%B4%20%EC%84%A4%EA%B3%84%EC%84%9C.pdf)



#  WBS
<details>
 <summary>WBS</summary>
 
 ![image](https://github.com/user-attachments/assets/5c2b0f10-e901-4541-9090-600982fafccd)
 
</details>




#  테스트 계획 및 결과 보고서 
<details>
 <summary>테스트 계획 및 결과보고서 </summary> 

### <테스트 계획>
   
![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0001](https://github.com/user-attachments/assets/c05cb468-e338-478f-b98a-a61128bd611b)
  
![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0002](https://github.com/user-attachments/assets/8c67cb6d-8758-4577-a82e-64c4f7c978d1)

![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0003](https://github.com/user-attachments/assets/e5ffaf14-6440-4354-a32f-edea5be3bc84)


   
### <테스트 결과>
 ![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0008](https://github.com/user-attachments/assets/88892af8-a4c1-4a91-83fa-f98e31f7bd61)
![9기-2팀_모델 테스트 계획 및 결과 보고서_page-0009](https://github.com/user-attachments/assets/8760f02a-3fc5-491c-b8b0-83f34b8ec9e2)


</details>

[테스트 계획 및 결과 보고서 자세히 보러가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN09-FINAL-2Team/blob/main/docs/9%EA%B8%B0-2%ED%8C%80_%EB%AA%A8%EB%8D%B8%20%ED%85%8C%EC%8A%A4%ED%8A%B8%20%EA%B3%84%ED%9A%8D%20%EB%B0%8F%20%EA%B2%B0%EA%B3%BC%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf)


#  수행결과(테스트/시연 페이지)


# 회고
