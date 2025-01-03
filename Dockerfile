FROM python:3.13-alpine

RUN addgroup --gid 20001 --system nonroot && \
    adduser --uid 10001 --system --ingroup nonroot --disabled-password --no-create-home --gecos "" nonroot && \
    pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=nonroot:nonroot src src
RUN mkdir /history && chown nonroot:nonroot /history
VOLUME /history

USER nonroot:nonroot

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

ENTRYPOINT ["python", "/src/main.py"]
