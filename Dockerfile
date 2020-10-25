FROM python:slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./chi_tg_inline_bot ./chi_tg_inline_bot
CMD ["python", "-m", "chi_tg_inline_bot.__main__"]
