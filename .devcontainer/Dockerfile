FROM gcr.io/gem5-test/hpca-23-gem5-build:latest as source

FROM gcr.io/gem5-test/ubuntu-22.04_all-dependencies:latest

RUN apt -y update && apt -y install git

COPY --from=source /gem5/build/ALL/gem5.fast /usr/local/bin/gem5
