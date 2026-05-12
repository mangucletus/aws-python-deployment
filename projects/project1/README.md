# How To Deploy Python Application In AWS?

We will explore how one, as a Python developer, can deploy an application by harnessing the capabilities of AWS. AWS, a leading cloud computing platform, offers a wide range of services to help developers build, deploy, and manage applications at scale.

EC2 provides scalable computing power in the cloud, allowing developers to scale up or down depending on application demand. We will use the **EC2 (Elastic Compute Cloud)** service provided by AWS to make our server and run our application on it.

## Why Deploy Python Applications On AWS?

- **Scalability:** AWS provides a scalable infrastructure, allowing your Python application to easily handle multiple tasks.
- **Elastic Beanstalk:** AWS Elastic Beanstalk is a Platform-as-a-Service (PaaS) offering that simplifies the deployment and management of Python applications.
- **Reliability and Availability:** AWS offers global connectivity across data centers, ensuring a high level of reliability for your Python application.

## Step-By-Step Guide To Deploy Python Applications In AWS

### Step 1: Log In To AWS

Log in with your AWS account credentials and navigate to the **AWS Management Console**.

### Step 2: Search For EC2

After signing in, you will land on the AWS Management Console page. Search for **EC2**.

*(AWS Console)*

### Step 3: Open EC2 Instances

This will take you to the Amazon EC2 dashboard. From there, select **Instances** from the left menu.

*(EC2 Dashboard)*

### Step 4: Launch An Instance

From the top right, select **Launch Instances**. This will allow you to create an EC2 instance (server). This server will contain all the necessary files needed to deploy your application.

*(Launching Instances)*

### Step 5: Name & Choose An OS Image

Give a name to your server and select an OS image (AMI) — for example, **Ubuntu**. You can also choose another image. This OS image gives you the ability to interact with the server.

*(Defining the Instance)*

### Step 6: Configure Network Settings

Select the default key-pair name and check the box for **HTTP/HTTPS**. This will allow you to test your application over the HTTP/HTTPS protocol.

*(Configuring Network Settings)*

### Step 7: Launch The Instance

Launch the instance from the bottom right corner. After that, you should see the status as **Success**.

*(Create Instance)*

### Step 8: Connect To Your Instance

Go to your instances and select the checkbox next to your instance name. From the top menu, select **Connect**. This will let you connect to the server.

*(Connecting To EC2 Instance)*

### Step 9: Open The Console

Keep the settings as they are and click **Connect**. This will connect your OS with the server.

*(Connecting EC2 Instance Console)*

### Step 10: Clone Your Repository

This will open the Ubuntu terminal. Clone your project's GitHub repository into the server. Provide the GitHub URL of your Python application:

```bash
git clone <your_github_repository_url>
```

*(Clone repo)*

### Step 11: Move Into The Repo Directory

Move into the cloned Git repo directory using the `cd` command:

```bash
cd <folder_path>
```

*(Navigate to the downloaded repo)*

### Step 12: Update Packages

Update the existing packages on the server using the following command:

```bash
sudo apt update
```

*(Update packages)*

### Step 13: Install pip

Install `pip` for Python 3 on the server so you can install your packages. Press **yes** for any prompt:

```bash
sudo apt install python3-pip
```

*(Install pip3)*

### Step 14: Install Dependencies

Install all the dependencies on your server using `requirements.txt`. If it is not present in your project, create it.

```bash
pip3 install -r requirements.txt
```

*(Installing from requirements.txt file)*

### Step 15: Run Your Application

Now run your application. How you run it depends on the tech stack used to build the application. In this case, it's FastAPI, so just directly run `main.py`.

Also copy the **public IP** from below and the **port number** (e.g., 8000). At this IP your app will be hosted.

*(Run application)*

### Step 16: Access The Deployed App

Open a new tab and enter your IP with the port number separated by a colon (`:`):

```
<public_ip>:<port_number>
```

*(Accessing Deployed Application)*

## Conclusion

In this article, we deployed a Python application on AWS using the EC2 service provided by AWS. We used a GitHub repo and cloned our code onto the server, installed the required packages, and then ran the application — making it live at the IP provided by AWS.
