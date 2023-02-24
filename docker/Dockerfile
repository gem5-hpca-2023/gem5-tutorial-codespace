FROM gcr.io/gem5-test/ubuntu-22.04_all-dependencies:latest

RUN apt -y update && apt -y install git

RUN git clone https://gem5.googlesource.com/public/gem5 /gem5

WORKDIR /gem5

RUN git checkout 3bb19be083d38249d1e1652184d05b0e6406a660

RUN scons -j`nproc` build/ALL/gem5.fast


