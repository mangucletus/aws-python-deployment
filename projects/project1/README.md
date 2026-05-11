# How To Deploy Python Application In AWS?

This guide explores how a Python developer can deploy applications using AWS. AWS is a leading cloud computing platform offering a wide range of services to build, deploy, and manage applications at scale. We use the **EC2 (Elastic Compute Cloud)** service to provision a server and run our application on it.

## Why Deploy Python Applications On AWS?

- **Scalability:** AWS provides scalable infrastructure that lets your Python application handle multiple tasks easily.
- **Elastic Beanstalk:** A Platform-as-a-Service (PaaS) offering that simplifies deployment and management of Python applications.
- **Reliability and Availability:** Global data center connectivity ensures high reliability for your application.

## Step-By-Step Guide To Deploy Python Applications In AWS

**Step 1:** Log in to your AWS account and navigate to the AWS Management Console.

**Step 2:** From the AWS Management Console, search for **EC2**.

**Step 3:** On the Amazon EC2 dashboard, select **Instances** from the left menu.

**Step 4:** Click **Launch Instances** from the top right to create an EC2 instance (server) that will host your application files.

**Step 5:** Give your server a name and select an OS image (AMI) — for example, **Ubuntu**. This OS image enables you to interact with the server.

**Step 6:** Select the default key-pair name and check the **HTTP/HTTPS** boxes to allow testing your application over those protocols.

**Step 7:** Click **Launch Instance** at the bottom right. You should see a success status.

**Step 8:** Go to your instances, select your instance by name, and click **Connect** from the top menu.

**Step 9:** Keep the default settings and click **Connect** to open a session with the server.

**Step 10:** In the Ubuntu terminal, clone your project's GitHub repository:

```bash
git clone <your_github_repository_url>
```

**Step 11:** Navigate into the cloned repository:

```bash
cd <folder_path>
```

**Step 12:** Update the server's package list:

```bash
sudo apt update
```

**Step 13:** Install pip for Python 3 (confirm with "yes" at any prompt):

```bash
sudo apt install python3-pip
```

**Step 14:** Install all project dependencies from `requirements.txt` (create one if it doesn't exist):

```bash
pip3 install -r requirements.txt
```

**Step 15:** Run your application. The command depends on your tech stack — for FastAPI, run `main.py` directly. Note the **public IP** and **port number** (e.g., 8000) where your app will be hosted.

**Step 16:** Open a new browser tab and visit your app at:

```
<public_ip>:<port_number>
```

## Conclusion

In this guide, we deployed a Python application on AWS using the EC2 service. We cloned our code from GitHub onto the server, installed the required packages, and launched the application — making it live at the public IP provided by AWS.
