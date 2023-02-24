This directory provides the source for building the gcr.io/gem5-test/hpca-23-gem5-build image.
This is a base image used in ".devcontainer/Dockerfile" to obtain the a compiled version of gem5.

## Building

gcr.io/gem5-test/hpca-23-gem5-build can be built by executing:

```sh
docker-compose build hpca-23-gem5-build
```

## Notes for developers
These images can be pushed with: `docker-compose push`.
Permission must be granted to push to the Google Cloud repository before doing so.

The Dockerfile tags must be updated accordingly for each release of gem5.
