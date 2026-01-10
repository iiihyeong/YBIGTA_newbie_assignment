
# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!

MINICONDA_PATH="$HOME/miniconda"

if [ -d "$MINICONDA_PATH" ]; then
    echo "[INFO] Miniconda가 이미 설치되어 있습니다 ($MINICONDA_PATH). 설정을 로드합니다."
    source "$MINICONDA_PATH/bin/activate"
elif ! command -v conda &> /dev/null; then
    echo "[INFO] Conda가 없습니다. Miniconda 설치를 시작합니다..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -u -p "$MINICONDA_PATH"
    source "$MINICONDA_PATH/bin/activate"
    conda init
    rm miniconda.sh
else
    echo "[INFO] 시스템에 Conda가 감지되었습니다."
fi


# Conda 환셩 생성 및 활성화

eval "$(conda shell.bash hook)"

if ! conda env list | grep -q "myenv"; then
    echo "[INFO] 'myenv' 가상환경을 생성합니다..."
    conda create -n myenv python=3.10 -y
else
    echo "[INFO] 'myenv' 가상환경이 이미 존재합니다."
fi

conda activate myenv

## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi

# 필요한 패키지 설치
pip install -q mypy

# Submission 폴더 파일 실행

cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    filename="${file%.*}"
    
    echo "[RUN] $file 실행 중..."

    python "$file" < "../input/${filename}_input" > "../output/${filename}_output"
    
done

# mypy 테스트 실행 및 mypy_log.txt 저장
echo "[INFO] Mypy 테스트 수행 중..."
mypy . > ../mypy_log.txt

# conda.yml 파일 생성
echo "[INFO] 환경 정보 내보내기 중..."
conda env export > ../conda.yml

# 가상환경 비활성화
conda deactivate
echo "[INFO] 모든 작업 완료"