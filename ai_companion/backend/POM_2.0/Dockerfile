FROM python:3.11-slim

WORKDIR /app

# Set environment variables to accept TTS TOS automatically
ENV COQUI_TOS_AGREED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8007

CMD ["python", "phonatory_api.py"]