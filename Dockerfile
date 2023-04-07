FROM python:3.11.3-slim
ARG APPDIR="/home/app"
ENV PATH="${APPDIR}/.local/bin:${PATH}"
ENV PROOVR_ICS_UID=1000
ENV PROOVR_ICS_GID=1000
RUN addgroup --gid ${PROOVR_ICS_UID} --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid ${PROOVR_ICS_GID} --system --group app
RUN mkdir ${APPDIR} && chown -R ${PROOVR_ICS_UID}:${PROOVR_ICS_GID} ${APPDIR}
USER app
WORKDIR ${APPDIR}
COPY --chown=${PROOVR_ICS_UID}:${PROOVR_ICS_GID} requirements.txt ${APPDIR}
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=${PROOVR_ICS_UID}:${PROOVR_ICS_GID} . ${APPDIR}
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app.__init__:app"]
