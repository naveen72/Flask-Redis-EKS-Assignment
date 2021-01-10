# Flask-Redis-EKS-Assignment

In This assignment, we'll be deploying Flask App and redis storage as 2 separate service in EKS cluster.
Below are the steps, which we would be folloing sequenntially:

Step1: Create EKS Service Linked IAM role
========================================

Please run cloudformation template ServiceRole.yml, it will create one service linked role, which we'll assume while running cloudformation template to provision EKS Cluster.
Also, same IAM role we'll be adding with Jump server. By doing this, we'll be able to manage cluster via jump server.

```
ServiceRole.yml
```
Step2: Create Worker Node IAM role
=================================

Run cloudformation template NodeIAMRole.yml, it will create one worker node IAM role, which will be added to NodeGroup of EKS Worker Node.
```
NodeIAMRole.yml
```
Step3: Create EKS Cluster
=========================

Run cloudformation template EKS-Cluster.yml, it will create EKS Cluster and version will be 1.16. We can select the EKS version during cloudformation launch time.
```
Note: Assume Service Role created in Step1, which launching this EKS cluster stack using template EKS-Cluster.yml"
```
Step4: Provison Worker Nodes
============================
Run cloudformaton template amazon-eks-nodegroup.yaml to provison the worker nodes. Select parameters properly while launching the stack.
```
amazon-eks-nodegroup.yaml
```
