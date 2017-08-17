FROM python:3.6.2-alpine

WORKDIR app
COPY requirements.txt /app/requirements.txt

# build dependencies
RUN \
apk add --update --no-cache --virtual=build-deps \
    ca-certificates \
    freetype-dev \
    g++ \
    gcc \
    lcms2-dev \
    libffi-dev \
    libjpeg-turbo-dev \
    libwebp-dev \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    make \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev && \

# runtime dependencies
apk add --update --no-cache \
    freetype \
    lcms2 \
    libjpeg-turbo \
    libwebp \
    libxml2 \
    libxslt \
    openjpeg \
    su-exec \
    tiff && \

# pip packages
pip install --no-cache-dir -U \
    pip && \
pip install --no-cache-dir -r \
    requirements.txt && \

# cleanup
apk del --purge \
    build-deps && \
rm -rf \
    /tmp/*

COPY . /app/
# move these user modifiable folders so we can copy them to the volume mounts later
# no way to do these in a single layer unfortunately
COPY cogs /app/.sample/cogs
COPY settings /app/.sample/settings
COPY anims /app/.sample/anims

VOLUME /app/cogs /app/settings /app/anims
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-u", "loopself.py"]

