# micro sidecar

The **micro sidecar** is a service mesh for building highly available and fault tolerant microservices.

It is similar to Netflix's sidecar [Prana](https://github.com/Netflix/Prana), Buoyant's RPC Proxy [Linkerd](https://linkerd.io) 
or Lyft's [Envoy](https://lyft.github.io/envoy/).

The micro sidecar builds on [go-micro](https://github.com/micro/go-micro) with the same defaults and pluggability.

<p align="center">
  <img src="https://github.com/micro/docs/blob/master/images/car.png" />
</p>

Example usage in many languages can be found at [examples/sidecar](https://github.com/micro/examples/tree/master/sidecar)

## API

The sidecar has the following HTTP api

```
- /[service]/[method]
- /broker
- /registry
- /rpc
```

## Features

The sidecar has all the features of [go-micro](https://github.com/micro/go-micro). Here are the most relevant.

- Service Discovery
- Message Broker
- RPC and Proxy Handlers
- Load balancing, retries, timeouts
- Healthchecking
- Stats UI
- Pluggable via go-micro

## Getting Started

### Install

```shell
go get github.com/micro/micro
```

### Deps

The sidecar uses go-micro which means it has one default dependency, consul for service discovery.

```
brew install consul
consul agent -dev
```

### Run

The micro sidecar runs on port 8081 by default. 

Starting the sidecar 

```shell
micro sidecar
```

Optionally specify app server name and address if you want to auto register an app on startup.

```shell
micro sidecar --server_name=foo --server_address=127.0.0.1:9090
```

### ACME via Let's Encrypt

Serve securely by default using ACME via letsencrypt 

```
micro --enable_acme sidecar
```

Optionally specify a host whitelist

```
micro --enable_acme --acme_hosts=example.com,api.example.com sidecar
```

### Serve Secure TLS

The Sidecar supports serving securely with TLS certificates

```bash
micro --enable_tls --tls_cert_file=/path/to/cert --tls_key_file=/path/to/key sidecar
```

### Auto Healthcheck

Start micro sidecar with "--healthcheck_url=" to enable the healthchecker

It does the following:
- Automatic service registration
- Periodic HTTP healthchecking
- Deregistration on non-200 response

```shell
micro sidecar --server_name=foo --server_address=127.0.0.1:9090 \
	--healthcheck_url=http://127.0.0.1:9090/health
```

## Registry

### Register Service

```shell
// specify ttl as a param to expire the registration
// units ns|us|ms|s|m|h
// http://127.0.0.1:8081/registry?ttl=10s

curl -H 'Content-Type: application/json' http://127.0.0.1:8081/registry -d 
{
	"Name": "foo.bar",
	"Nodes": [{
		"Port": 9091,
		"Address": "127.0.0.1",
		"Id": "foo.bar-017da09a-734f-11e5-8136-68a86d0d36b6"
	}]
}
```

### Deregister Service

```shell
curl -X "DELETE" -H 'Content-Type: application/json' http://127.0.0.1:8081/registry -d 
{
	"Name": "foo.bar",
	"Nodes": [{
		"Port": 9091,
		"Address": "127.0.0.1",
		"Id": "foo.bar-017da09a-734f-11e5-8136-68a86d0d36b6"
	}]
}
```

### Get Service

```shell
curl http://127.0.0.1:8081/registry?service=go.micro.srv.example
{
	"name":"go.micro.srv.example",
	"nodes":[{
		"id":"go.micro.srv.example-c5718d29-da2a-11e4-be11-68a86d0d36b6",
		"address":"[::]","port":60728
	}]
}
```

## Handlers

### RPC

Query micro services using json or protobuf. Requests to the backend will be made using the go-micro RPC client.

**Using /[service]/[method]**

Default namespace of services called are **go.micro.srv**

```shell
curl -H 'Content-Type: application/json' -d '{"name": "John"}' http://127.0.0.1:8081/example/call
```

**Using /rpc endpoint**

```shell
curl -d 'service=go.micro.srv.example' \
	-d 'method=Example.Call' \
	-d 'request={"name": "John"}' http://127.0.0.1:8081/rpc
```

### Proxy

Like the api and web servers, the sidecar can provide a full http proxy.

Enable proxy handler on the command line

```shell
micro sidecar --handler=proxy
```

The first element in the url path will be used along with the namespace as the service to route to.

## Request Mapping

URL Path mapping is the same as the micro API

Mapping of URLs are as follows:

Path	|	Service	|	Method
----	|	----	|	----
/foo/bar	|	go.micro.srv.foo	|	Foo.Bar
/foo/bar/baz	|	go.micro.srv.foo	|	Bar.Baz
/foo/bar/baz/cat	|	go.micro.srv.foo.bar	|	Baz.Cat

Versioned API URLs can easily be mapped to service names:

Path	|	Service	|	Method
----	|	----	|	----
/foo/bar	|	go.micro.srv.foo	|	Foo.Bar
/v1/foo/bar	|	go.micro.srv.v1.foo	|	Foo.Bar
/v1/foo/bar/baz	|	go.micro.srv.v1.foo	|	Bar.Baz
/v2/foo/bar	|	go.micro.srv.v2.foo	|	Foo.Bar
/v2/foo/bar/baz	|	go.micro.srv.v2.foo	|	Bar.Baz


## Broker

### Publish

```
curl -XPOST \
	-H "Timestamp: 1499951537" \
	-d "Hello World!" \
	"http://localhost:8081/broker?topic=foo"
```

### Subscribe

```go
conn, _, _ := websocket.DefaultDialer.Dial("ws://127.0.0.1:8081/broker?topic=foo", make(http.Header))

// optionally specify "queue=[queue name]" param to distribute traffic amongst subscribers
// websocket.DefaultDialer.Dial("ws://127.0.0.1:8081/broker?topic=foo&queue=group-1", make(http.Header))

for {
	// Read message
	_, p, err := conn.ReadMessage()
	if err != nil {
		return
	}

	// Unmarshal into broker.Message
	var msg *broker.Message
	json.Unmarshal(p, &msg)

	// Print message body
	fmt.Println(msg.Body)
}
```

## CLI Proxy

The sidecar also acts as a proxy for the CLI to access remote environments

```shell
$ micro --proxy_address=127.0.0.1:8081 list services
go.micro.srv.greeter
```

## Stats Dashboard

Enable a stats dashboard via the `--enable_stats` flag. It will be exposed on /stats.

```shell
micro --enable_stats sidecar
```

<img src="https://github.com/micro/docs/blob/master/images/stats.png">
