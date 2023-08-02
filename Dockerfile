FROM python:3.12.0b4-slim
ARG USERNAME="application"
ARG APPDIR="/home/${USERNAME}"
ENV PATH="${APPDIR}/.local/bin:${PATH}"
ENV PROOVR_ICS_UID=1000
ENV PROOVR_ICS_GID=1000
RUN groupadd --gid ${PROOVR_ICS_GID} ${USERNAME}
RUN useradd --uid ${PROOVR_ICS_UID} --groups ${PROOVR_ICS_GID} --shell /bin/false --create-home ${USERNAME}
RUN mkdir ${APPDIR} && chown -R ${PROOVR_ICS_UID}:${PROOVR_ICS_GID} ${APPDIR}
USER ${USERNAME}
WORKDIR ${APPDIR}
COPY --chown=${PROOVR_ICS_UID}:${PROOVR_ICS_GID} requirements.txt ${APPDIR}
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=${PROOVR_ICS_UID}:${PROOVR_ICS_GID} . ${APPDIR}
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app.__init__:app"]
