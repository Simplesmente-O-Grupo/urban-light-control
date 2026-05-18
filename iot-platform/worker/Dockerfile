FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /worker

RUN useradd \
	--shell /sbin/nologin \
	--uid 10001 \
	--no-create-home \
	mqtt-client-usr

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

USER mqtt-client-usr

COPY . .

CMD ["python3", "main.py"]
