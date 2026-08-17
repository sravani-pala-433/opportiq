FROM ubuntu:latest
LABEL authors="ravig"

ENTRYPOINT ["top", "-b"]