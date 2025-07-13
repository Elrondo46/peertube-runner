
# [`tuxnvape/peertube-runner`]

Containerized Node [`@peertube/peertube-runner`](https://www.npmjs.com/package/@peertube/peertube-runner) for
remote execution of transcoding jobs in Kubernetes.

```bash
docker run -it --rm -u root --name runner-server \
  -v $PWD/dot-local:/home/peertube/.local/share/peertube-runner-nodejs \
  -v $PWD/dot-config:/home/peertube/.config/peertube-runner-nodejs \
  -v $PWD/dot-cache:/home/peertube/.cache/peertube-runner-nodejs \
  tuxnvape/peertube-runner peertube-runner server
```
