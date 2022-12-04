# mobility-loadbalancer
A working L3 loadbalancer for Kubernetes using kindnetd.

## Description
Deployable via a Pod whose hostNetwork option is set to true. You may build your own image using the provided Dockerfile. But you also have the option to deploy a ready built image found at kismi/lb:latest on DockerHub.

The docker image contains the script needed for it to work, you need to provide the host network address to be used and the Home Agent IPs of the cluster.

The agent itself terminates by sending an ENOINT signal to the program. This will remove every change it made to its host device.
