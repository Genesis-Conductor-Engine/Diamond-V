FROM python:3.9-slim
WORKDIR /app
RUN pip install requests redis
COPY sync_orchestrator.py .
CMD ["python", "sync_orchestrator.py"]

# Install OpenCode AI CLI
RUN npm install -g opencode-ai

# Verify opencode installation
RUN which opencode && opencode --version
