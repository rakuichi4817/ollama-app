#==================================
# ベースイメージ
#==================================
FROM python:3.12-slim AS base

ARG workdir="/ollama-app"

RUN apt-get update && pip install --upgrade pip 

#==================================
# ビルダー
#==================================
FROM base AS builder

RUN pip install pipenv 
# ライブラリの情報を先にコピーし、システム側へのインストール
COPY ./Pipfile ./Pipfile.lock /
RUN pipenv sync --system


#==================================
# 開発環境（devcontainer接続用）
#==================================
FROM base AS devcontainer
# devcontainer上では仮想環境を作って開発する
RUN apt-get install -y git \
    && pip install pipenv

#==================================
# appイメージ
#==================================
FROM base AS app
WORKDIR $workdir

# ビルダーからのソース受け取り
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/streamlit /usr/local/bin/streamlit

# 作成したソースのコピー
COPY ./app ${workdir}/app

HEALTHCHECK CMD curl --fail <http://localhost:8501/_stcore/health>


EXPOSE 8501

ENTRYPOINT [ "streamlit",  "run", "app/main.py","--server.port=8501","--server.address=0.0.0.0" ]