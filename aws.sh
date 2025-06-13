# 1. 패키지 업데이트
sudo yum update -y

# 2. Docker 설치
sudo yum install -y docker libxcrypt-compat git # docker-compose
# sudo apt-get install -y docker libxcrypt-compat git # docker-compose

# 3. Docker 서비스 시작
sudo systemctl start docker

# 4. Docker 부팅 시 자동 시작
sudo systemctl enable docker

# 현재 사용자(ec2-user 등)를 docker 그룹에 추가하면 sudo 없이 docker 명령을 사용할 수 있습니다.
sudo usermod -aG docker $USER
# 변경 적용을 위해 재로그인 필요

# 5. 설치 확인
docker --version
# 1. Docker Compose 최신 버전 확인 (선택)
# 공식 릴리즈 확인: https://github.com/docker/compose/releases

# 2. Docker Compose 다운로드
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 3. 실행 권한 부여
sudo chmod +x /usr/local/bin/docker-compose

# 4. 심볼릭 링크 추가 (선택)
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 5. 설치 확인
docker-compose --version

scp -i ./senpick.pem -r ./qdrant_ad/qdrant_storage/  ubuntu@52.4.21.137:/home/ubuntu/

sudo yum update
sudo yum install certbot python3-certbot-nginx -y

sudo certbot --nginx -d senpick.kr

# cat your-private-key.pem | base64