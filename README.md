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
Note: Assume Service Role created in Step1, while launching this EKS cluster stack using template EKS-Cluster.yml"
```
Step4: Provison Worker Nodes
============================
Run cloudformaton template amazon-eks-nodegroup.yaml to provison the worker nodes. Select parameters properly while launching the stack.
```
amazon-eks-nodegroup.yaml
```
step5: Create ECR Repository
============================

Create ECR Repository to store Flask app and redis storage image using cloudformation template ECR.yml. This template will create separate registry for Flask app and redis storage
```
ECR.yml
```
step6: Create Jump Server 
==========================

Create a jump server to manage all EKS cluster related activity using kubectl command.
```
Jump_Server.yml
```
Note: Make sure to provide only Instance profile name of service role (created in step1), whole ARN is not required.

step7: awscli, kubectl & aws-iam-authenticator Installation 
==========================================================

Refer file AwsCli-Kubectl-Aws-IAM-Authenticator.md to do this configuration.
```
AwsCli-Kubectl-Aws-IAM-Authenticator.md
```
Also, install docker on jump server. 

Step8: Docker image Creation
============================

Run dockbuild on Dockerfile uploaded to create flask app image and perform below actvity.
```
docker build -t flaskapp:1 .
```
Tag with Repo address
```
docker tag flaskapp:latest 045959739851.dkr.ecr.us-east-1.amazonaws.com/flaskapp:latest
```
Login to ECR Repo
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 045959739851.dkr.ecr.us-east-1.amazonaws.com
```
Push image to repo
```
docker push 045959739851.dkr.ecr.us-east-1.amazonaws.com/flaskapp:latest
```
Push Redis docker image to ECR.
```
docker pull redis:alpine
docker tag redis:alpine 045959739851.dkr.ecr.us-east-1.amazonaws.com/redis:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 045959739851.dkr.ecr.us-east-1.amazonaws.com
docker push 045959739851.dkr.ecr.us-east-1.amazonaws.com/redis:latest
```
Step9: FlaskApp Deployment
============================

Refer flask-deployment.yml for flask_webapp deployment. We have used default namespace.
```
apiVersion: apps/v1beta2
kind: Deployment
metadata:
  name: flask_webapp
  namespace: default
  labels:
    run: flask_webapp
spec:
  replicas: 2
  selector:
    matchLabels:
      run: flask_webapp
  template:
    metadata:
      labels:
        run: flask_webapp
    spec:
      containers:
      - image: 045959739851.dkr.ecr.us-east-1.amazonaws.com/flaskapp:latest
        name: flask_webapp
        livenessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 300
          timeoutSeconds: 5
          periodSeconds: 300
          failureThreshold: 3
        ports:
          - containerPort: 5000
            name: http
            protocol: TCP
```
Note:
```
Here, in above code snippet,my ECR link is there. Update it before running. Also, as per requirement, we have no of replica as 2 for webapp
```
Step9: Redis Storage Deployment
============================
Refer redis-deployment.yml for Redis storage deployment.

```
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: redis
  namespace: default
spec:
  selector:
    matchLabels:
      run: flask_webapp
      role: master
      tier: backend
  replicas: 1
  template:
    metadata:
      labels:
        run: flask_webapp
        role: master
        tier: backend
    spec:
      containers:
      - name: redis
        image: 045959739851.dkr.ecr.us-east-1.amazonaws.com/redis:latest
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
        ports:
        - containerPort: 6379
```
Note:
```
Here, in above code snippet,my ECR link is there. Update it before running. Also, as per requirement, we have no of replica as 1 for Redis storage
```
Step10: Redis Storage Service
============================
Refer redis-deployment.yml for Redis storage deployment.
Reason for setting up service: Setted up redis instance, however it was not able to talk to each-other from separate , the setup worked over local machine with docker-compose but did not work with kubernetes. flask couldn't find the service, so the error was with  configuration files

Flask code:
```
redis = Redis(host='redis', port=6379)
```
So to fix this, we update flask_app.py with below lines:
```
redis = Redis(host='my-redis-svc.default.svc.cluster.local', port=6379)
```
And created below service object. Now pods should be accessible by other pods in same namespace using that hostname
```
my-redis-svc.default.svc.cluster.local
```
Redis-service.yml snippet:
```
apiVersion: v1
kind: Service
metadata:
  labels:
    app: redis
  name: my-redis-svc
  namespace: default
spec:
  ports:
  - name: redis
    port: 6379
    targetPort: 6379
    protocol: TCP
  selector:
    app: redis
  type: ClusterIP
```

As per the requirement, we have two pods for flask webapp and one for redis storage. This should work seemlessly. Webapp can be access using Pod_ip and port.

Thanks for your time.
