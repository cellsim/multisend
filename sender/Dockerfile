FROM ubuntu:20.04 as builder
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    git

WORKDIR /tmp

ARG SHA=LATEST

RUN SHA=${SHA}\
    git clone https://github.com/fuji246/multisend.git && \
    cd multisend && \
    cd sender && \
    make saturatr-flyio

# Create production image
FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    tcpdump \
    iperf3

COPY --from=builder /tmp/multisend/sender/saturatr-flyio /usr/local/bin/saturatr
COPY saturatr.conf /etc/nginx/conf.d/saturatr.conf

#ENTRYPOINT ["saturatr"]
CMD ["sh", "-c", "nginx && saturatr"]
