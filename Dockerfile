FROM python:3-bookworm
ARG USERNAME="app"
ARG APPDIR="/home/${USERNAME}"
ENV PATH="${APPDIR}/.local/bin:${PATH}"
ENV PROOVR_ICS_UID=1000
ENV PROOVR_ICS_GID=1000
RUN groupadd --gid ${PROOVR_ICS_GID} ${USERNAME} \
    && useradd --uid ${PROOVR_ICS_UID} --gid ${PROOVR_ICS_GID} --shell /bin/false --create-home ${USERNAME}
USER ${USERNAME}
WORKDIR ${APPDIR}
COPY --chown=${PROOVR_ICS_UID}:${PROOVR_ICS_GID} requirements.txt ${APPDIR}
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=${PROOVR_ICS_UID}:${PROOVR_ICS_GID} . ${APPDIR}
HEALTHCHECK --interval=60s --timeout=5s --retries=3 CMD curl --silent --output /dev/null --fail http://localhost:${PROOVR_ICS_PORT:-5000} || exit 1
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app.__init__:app"]
