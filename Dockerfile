FROM python:3
RUN mkdir app
WORKDIR /app
COPY . /app
ENTRYPOINT ["python", "./solution.py"]
CMD [""]