# **Deployment Scripts**

Scripts able to deploy an application through [rd-jenkins-pipeline](https://github.com/dorefactor/rd-jenkins-pipeline)

## **Prerequisites**

* Python 3 & Pip 3
* Ansible 2.8+

## **Manual Testing**

### **Services**

* [RegularApi](https://github.com/dorefactor/RegularApi)
* [rd-jenkins-builder](https://github.com/dorefactor/rd-jenkins-builder)

### **Commands**

* Generate ansible inventory

```sh
python deployer/deployer.py --deployment-order-id=${DEPLOYMENT_ORDER_ID} --api-url=${RD_API_URL} --build-inventory
```

* Run deployment

```sh
python deployer/deployer.py --execute
```