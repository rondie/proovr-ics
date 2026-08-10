FROM python:3-bookworm
ARG APPDIR="/home/app"
ENV PATH="${APPDIR}/.local/bin:${PATH}"
ENV UID=10001
ENV GID=10001
RUN groupadd --gid ${GID} app \
    && useradd --uid ${UID} --gid ${GID} --shell /bin/false --create-home app
USER 10001
WORKDIR ${APPDIR}
COPY --chown=${UID}:${GID} requirements.txt ${APPDIR}
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=${UID}:${GID} . ${APPDIR}
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --start-interval=5s --retries=3 CMD ["curl", "--silent", "--output", "/dev/null", "--fail", "http://localhost:${PROOVR_ICS_PORT:-5000}"]
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app.__init__:app"]
