# Build image
FROM gradle:8.7-jdk-graal-jammy AS builder
WORKDIR /src
ADD https://github.com/nordic-institute/X-Road/archive/refs/tags/7.5.1.tar.gz /src
RUN tar -xzf 7.5.1.tar.gz && rm 7.5.1.tar.gz
WORKDIR /src/X-Road-7.5.1/src
RUN apt-get update && apt-get install -y build-essential
RUN gradle -Dorg.gradle.jvmargs=-Xmx6g -PxroadBuildType=RELEASE --no-daemon build -x test -x intTest -x runProxyTest -x integrationTest -x runMetaserviceTest -x runProxymonitorMetaserviceTest -x jacocoTestReport -x checkstyleTest -x checkstyleMain -x e2eTest
COPY process.py .
RUN python3 process.py

# Runtime image 21 is not supported by X-Road
FROM eclipse-temurin:17-jre-noble AS runtime
RUN groupadd -r -g 1100 xroad && useradd -rM -g xroad -u 1100 xroad
USER xroad:xroad
COPY --from=builder /usr/share/xroad /usr/share/xroad
COPY --from=builder /usr/share/doc/ /usr/share/doc/
COPY --from=builder /etc/xroad/ /etc/xroad/
COPY --from=builder /var/lib/xroad/ /var/lib/xroad/
COPY --from=builder /etc/rsyslog.d/ /etc/rsyslog.d/

ENV LD_LIBRARY_PATH="/usr/share/xroad/lib:$LD_LIBRARY_PATH"
ENV ADDON_PATH="/usr/share/xroad/jlib/addon"

EXPOSE 8080 8443 4000 5500 5577 5588