FROM python:3.12-alpine
ARG APPDIR="/home/app"
ENV PATH="${APPDIR}/.local/bin:${PATH}"
ENV UID=10001
ENV GID=10001
RUN addgroup -g ${GID} app && \
    adduser -D -u ${UID} -G app -s /bin/false -h ${APPDIR} app
RUN apk add --no-cache curl=8.21.0-r0
USER 10001
WORKDIR ${APPDIR}
COPY --chown=${UID}:${GID} requirements.txt ${APPDIR}
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=${UID}:${GID} . ${APPDIR}
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --start-interval=5s --retries=3 CMD ["curl", "--silent", "--output", "/dev/null", "--fail", "http://localhost:5000"]
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app.__init__:app"]
