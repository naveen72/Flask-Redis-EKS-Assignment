awscli, kubectl and aws-iam-autheticator would be required on newly created jump server. Please follow below steps for installation:

Step1: Jump Server upgrade and Python/aws cli installation
==========================================================

Login to jump server, switch to root user mode and run below commands:
```
apt-get update
apt install python3.8 
apt-get install awscli 
```
step2: Kubectl and aws-iam-authentictor installation
====================================================
Note: This kubectl cofiguration done for EKS 1.16. Please refer https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html
Be in root user mode and run commands as shown below to install kubectl:
```
root@ip-172-31-88-33:/home/ubuntu# cd
root@ip-172-31-88-33:~# curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.15/2020-11-02/bin/linux/amd64/kubectl
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 55.8M  100 55.8M    0     0  5757k      0  0:00:09  0:00:09 --:--:-- 6573k
root@ip-172-31-88-33:~# chmod +x ./kubectl
root@ip-172-31-88-33:~# mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
root@ip-172-31-88-33:~# echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
root@ip-172-31-88-33:~# kubectl
```
Be in root user mode and run commands as shown below to install aws-iam-authenticator:
For detailed documentation, please refer https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html
```
root@ip-172-31-88-33:~# pwd
/root
root@ip-172-31-88-33:~# curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.18.9/2020-11-02/bin/linux/amd64/aws-iam-authenticator
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 33.6M  100 33.6M    0     0  5727k      0  0:00:06  0:00:06 --:--:-- 6776k
root@ip-172-31-88-33:~# chmod +x ./aws-iam-authenticator
root@ip-172-31-88-33:~# mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$PATH:$HOME/bin
root@ip-172-31-88-33:~# echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
root@ip-172-31-88-33:~# aws-iam-authenticator help
```

Now, we are good with the pre-requisites.

Step3: Configure cluster with Jump Server
==============================================
To create or update the kubeconfig file for cluster, run the following command:

```
aws eks --region region update-kubeconfig --name cluster_name
```
Note: Replace region with your AWS Region. Replace cluster_name with your cluster name. By default, the configuration file is created at the kubeconfig path ($HOME/.kube/config) in your home directory or merged with an existing kubeconfig at that location. 
```
Example:
root@ip-172-31-88-33:/home/ubuntu# cd
root@ip-172-31-88-33:~# aws eks --region us-east-1 update-kubeconfig --name EKSCL-01
Added new context arn:aws:eks:us-east-1:045959739851:cluster/EKSCL-01 to /root/.kube/config
```
To test your configuration, run the following command:
```
kubectl get svc
```
Example:
```
ubuntu@ip-172-31-88-33:~$ sudo su
root@ip-172-31-88-33:/home/ubuntu# cd
root@ip-172-31-88-33:~# aws eks --region us-east-1 update-kubeconfig --name EKSCL-01
Added new context arn:aws:eks:us-east-1:045959739851:cluster/EKSCL-01 to /root/.kube/config
root@ip-172-31-88-33:~# kubectl get svc
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.100.0.1   <none>        443/TCP   32m
```
 
Step4: Add worker nodes to the Amazon EKS cluster
=================================================

Once the control plane of cluster has been activated, the next step is to add nodes to it. To do this, we configure aws-auth ConfigMap. It helps in adding nodes to join cluster, but we also use this ConfigMap to add RBAC access to IAM users and roles.

Download this home of root user, edit, and apply the AWS authenticator configuration map.
```
curl -o aws-auth-cm.yaml https://s3.us-west-2.amazonaws.com/amazon-eks/cloudformation/2020-10-29/aws-auth-cm.yaml
```
Open the file in text editor. Replace <ARN of instance role (not instance profile)> with the Amazon Resource Name (ARN) of the IAM role associated with worker nodes, and save the file. Do not modify any other lines in this file. 

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: <ARN of instance role  (not instance profile)- Worker Node IAM Role>
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```
After updating the ARN, run below commands to apply it.

```
kubectl apply -f aws-auth-cm.yaml
```

Watch the status of your nodes and wait for them to reach the Ready status. 
```
kubectl get nodes
kubectl get nodes --watch
```
Example:
```
root@ip-172-31-88-33:~# kubectl get nodes
NAME                            STATUS     ROLES    AGE   VERSION
ip-172-31-29-79.ec2.internal    NotReady   <none>   7s    v1.10.3
ip-172-31-47-106.ec2.internal   NotReady   <none>   7s    v1.10.3
ip-172-31-84-159.ec2.internal   NotReady   <none>   11s   v1.10.3
```
For more details, please refer https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html
