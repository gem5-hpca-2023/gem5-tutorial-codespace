FROM gcr.io/gem5-test/ubuntu-22.04_all-dependencies:latest as source

RUN apt -y update && apt -y install git

RUN git clone https://gem5.googlesource.com/public/gem5 /gem5

WORKDIR /gem5

RUN scons -j`nproc` build/ALL/gem5.fast

FROM gcr.io/gem5-test/ubuntu-22.04_all-dependencies:latest
COPY --from=source /gem5/build/ALL/gem5.fast /usr/local/bin/gem5
