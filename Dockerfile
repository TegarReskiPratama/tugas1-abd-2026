FROM python:3.12.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    JUPYTER_PLATFORM_DIRS=1

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && useradd --create-home --uid 1000 jovyan \
    && mkdir -p /home/jovyan/work \
    && chown jovyan:jovyan /home/jovyan/work

WORKDIR /home/jovyan/work
COPY --chown=jovyan:jovyan . /home/jovyan/work
USER jovyan
EXPOSE 8888

# JupyterLab meminta token yang tercetak pada log container.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--ServerApp.root_dir=/home/jovyan/work"]

