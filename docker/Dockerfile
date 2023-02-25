FROM gcr.io/gem5-test/ubuntu-22.04_all-dependencies:latest

RUN apt -y update && apt -y install git

RUN git clone https://gem5.googlesource.com/public/gem5 /gem5

WORKDIR /gem5

RUN git checkout cd35c9a6194451952735f58fb09cb7983e5861ba

RUN scons -j`nproc` build/ALL/gem5.fast


