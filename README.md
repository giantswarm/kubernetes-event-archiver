[![Docker Automated build](https://img.shields.io/docker/automated/giantswarm/kubernetes-event-archiver.svg)](https://hub.docker.com/r/giantswarm/kubernetes-event-archiver/)

# kubernetes-event-archiver

A little service that reads events from the Kubernetes API and writes them to ElasticSearch.

It is assumed that ElasticSearch is running in the same namespace and accessible via hostname `elasticsearch` and port `9200` via HTTP. (This could easily be made configurable using environment variables.)

The kubernetes API is accessed via the hostname `kubernetes.default.svc`, so the according service is needed in namespace `default`.

To avoid archiving exact duplicates, the archiver creates an ID for each event to store, based on the content.

## Kubernetes Deployment

This will add the Deployment to the namespace `logging`:

```nohighlight
kubectl apply -f manifests/deployment.yaml
```

or, of you want to save yourself from cloning the repository:

```nohighlight
kubectl apply -f https://raw.githubusercontent.com/giantswarm/kubernetes-event-archiver/master/manifests/deployment.yaml
```
