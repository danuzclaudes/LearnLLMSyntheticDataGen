# Website and User Browsing Behavior Data Generator using LLM
A Proof-of-Concept project to simulate user web browsing behavior. All contents are generated via LLM.
The purpose of the project is to learn and connect knowledge across AWS, networking, and LLM.

Goal:
1. host a website using EC2 instance (Free-Tier), Route53, and GoDaddy
2. design and build LLM-based synthetic data generator
3. simulate synthetic user interactions on the given website

Synthetic Data Gen (SDG):
1. website & assets (html, css, images) [link](myapp/generators/webapp)
2. 150 synthetic user profiles for simulation [link](myapp/generators/interactions/user_profiles_generator.py)
3.  50 synthetic user behavior patterns (e.x. move mouse, scroll up/down, optional click, pause, etc) [link](myapp/generators/interactions/user_behavior_data_generator.py)
4. 495 synthetic user interactions by selecting X user profiles and Y user behavior patterns via LLM [link](myapp/generators/interactions/user_interactions_data_generator.py)
   LLM also provides an explanation for why making the choice.
5. 100 scripts to simulate user interactions on browser/webapp [link](myapp/generators/interactions/user_interactions_llm_interaction_scripts_generator.py)

Engineering Steps:
1. launch EC2 instance
2. install python3.10 on EC2 instance
3. host a basic flask app on EC2 instance using Nginx
4. setup OpenAI API
5. register DNS in GoDaddy and Route53
6. setup SSL in Nginx using certbot
7. publish website
8. Design Synthetic Data Generation
9. Generate synthetic data


------------------------------------------------------------

## Step 1. launch ec2 instance
```bash
aws ec2 create-security-group --group-name "cz-sg-1" --description "cz-sg-1 created 2024-11-24T22:27:21.939Z" --vpc-id "vpc-0ab9874cd34b8aa8d" 
aws ec2 authorize-security-group-ingress --group-id "sg-preview-1" --ip-permissions '{"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"<your-ip>/32"}]}' '{"IpProtocol":"tcp","FromPort":80,"ToPort":80,"IpRanges":[{"CidrIp":"0.0.0.0/0","Description":"HTTP web traffic"}]}' '{"IpProtocol":"tcp","FromPort":443,"ToPort":443,"IpRanges":[{"CidrIp":"0.0.0.0/0","Description":"HTTPS secure web traffic"}]}' '{"IpProtocol":"tcp","FromPort":5000,"ToPort":5000,"IpRanges":[{"CidrIp":"0.0.0.0/0","Description":"port for web app"}]}' 
aws ec2 run-instances --image-id "ami-0453ec754f44f9a4a" --instance-type "t2.micro" --key-name "cz-aws-default-key" --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-preview-1"]}' --credit-specification '{"CpuCredits":"standard"}' --metadata-options '{"HttpEndpoint":"enabled","HttpPutResponseHopLimit":2,"HttpTokens":"required"}' --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' --count "1"
```

### example Security Group Configuration
```log
Type	Protocol	Port Range	Source
SSH	TCP	22	My IP
HTTP	TCP	80	0.0.0.0/0
HTTPS	TCP	443	0.0.0.0/0
Custom TCP	TCP	5000	0.0.0.0/0  -> port for local flask app
Custom TCP  TCP 8000    0.0.0.0/0 -> port for Gunicorn web server
```

### error: permission 0555 are too open
```bash
ssh -i ~/cz-aws-default-key.pem ec2-user@<ip>.compute-1.amazonaws.com
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0555 for 'cz-aws-default-key.pem' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "cz-aws-default-key.pem": bad permissions
ec2-user@<public-ip>.compute-1.amazonaws.com: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).

=> chmod 400 cz-aws-default-key.pem


cz@DESKTOP-CZ:~$ ssh -i "cz-aws-default-key.pem" ec2-user@<ip>.compute-1.amazonaws.com
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
```

------------------------------------------------------------

## Step 2. install python3.10 on EC2 instance

```bash
sudo dnf update -y
sudo dnf groupinstall "Development Tools" -y
sudo dnf install gcc openssl-devel bzip2-devel libffi-devel zlib-devel -y
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.10.8/Python-3.10.8.tgz
sudo tar xzf Python-3.10.8.tgz
cd Python-3.10.8
sudo ./configure --enable-optimizations && sudo make altinstall
python3.10 --version
sudo python3.10 -m ensurepip --upgrade
python3.10 -m pip --version
pip3 --version
python3.10 -m pip install --upgrade pip
**sudo ln -sf /usr/local/bin/python3.10 /usr/bin/python** -> don't use /usr/bin/python3; it seems that python3 is reserved for dnf on ec2

pip install flask
```

------------------------------------------------------------

## Step 3. host a basic flask app on EC2 instance using Nginx
- Flask 101: as poc, first create app.py and index.html with the following directory tree:
```
myapp/
├── app.py
└── templates/
    └── index.html
```

- create basic app.py
```bash
mkdir myapp && cd myapp && touch app.py && cat > app.py <<EOF
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
EOF
```

- create basic index.html

```html
mkdir myapp/templates && cd templates && touch index.html && cat > index.html <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My First Flask Webpage</title>
</head>
<body>
    <h1>Welcome to My Website!</h1>
    <p>This is a simple Flask web application hosted on an EC2 instance.</p>
</body>
</html>
EOF
```

- test run app.py 
  - python3.10 ~/myapp/app.py 
  - => http://<public-ip>:5000
- sudo python3.10 -m pip install gunicorn 
- gunicorn --workers 3 --bind 0.0.0.0:8000 myapp.app:app
  - app:app tells Gunicorn to look for a Python module called app.py and within that module, use the Flask instance named app 
  - => http://<public-ip>:8000/
- sudo yum install nginx -y 
- sudo vim /etc/nginx/nginx.conf

```nginx
    server {
        listen 80;
        server_name <public-ip>;

        location / {
            proxy_pass http://127.0.0.1:8000;  # Forward requests to Gunicorn
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            root /home/ec2-user/myapp/app.py;
        }
    }
```

- sudo systemctl start nginx
- sudo systemctl enable nginx  # To start nginx automatically on boot
  - => http://<public-ip>/

### run app again for local testing:

```bash
python3.10 ~/myapp/app.py
sudo systemctl restart nginx
pkill gunicorn && ps aux | grep gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 myapp.app:app
sudo systemctl restart nginx
```

### role of Gunicorn
- Gunicorn: Python WSGI HTTP server that serves Python web applications
- A WSGI server, like Gunicorn, is responsible for
  - receiving HTTP requests from the web server (e.g., Nginx) and forwarding them to the Python application.
  - taking the response from the Python application and sends it back to the web server, which then sends it to the client (e.g., the user's browser).

### role of Nginx
1. Acts as a reverse proxy: It forwards requests to Gunicorn, making your app accessible over the internet.
2. Improves performance: By handling static file serving and enabling caching, Nginx reduces the load on Gunicorn.
3. Enhances security: By handling SSL/TLS, firewall protection, and rate-limiting.

------------------------------------------------------------

## Step 4. setup OpenAI API
https://platform.openai.com/docs/quickstart
1. create API key: https://platform.openai.com/api-keys
2. pip3 install openai
3. python openai-test.py
4. fix openai billing
5. in app.py, call API with test prompt


### Use OpenAI for better index.html
- prompt:

```text
Create a single-page website for a car purchasing and selling business. The website should be modern, visually appealing, and responsive. The design should include all HTML, CSS, and JavaScript in a single file, with the following sections and features:

Header/Nav Bar: A sticky navigation bar at the top of the page with links to Home, About, Stocks, and Contact sections. Smooth scroll functionality should allow users to jump between sections.

Hero Section: A full-screen background image with an overlay for text contrast. The background image path will be passed dynamically from the Flask Python app as hero_image_path. In the HTML, the image should be referenced using a structure like url("{{ url_for('static', filename=hero_image_path) }}"). Include a title with a smooth fade-in animation and a brief introduction beneath the title with a slide-in effect.

About Section: A section with a short biography of the business owner or company. Display a photo on the left with a zoom-in effect on hover and text on the right.

Stocks Section: A grid layout showing 3-5 car models. Each model should have a thumbnail image, a title, and a description that appears on hover. Clicking an image should open a larger version using a lightbox effect.

Contact Section: A simple contact form with fields for Name, Email, and Message, along with a Submit button. The form should include client-side validation to ensure all fields are filled out before submission.

Footer: A sticky footer with social media icons for platforms like Facebook, Twitter, and Instagram, along with copyright information.

CSS Design: Use modern CSS techniques like Flexbox or Grid for responsiveness. The design should adapt to different screen sizes, including mobile and tablet. Choose a clean, minimalist color scheme with two or three complementary colors for a professional look.

Animations: Add smooth animations such as fade-ins, slide-ins, or scaling effects for sections as users scroll. Use a lightweight JavaScript library like AOS or native JavaScript with IntersectionObserver to trigger animations.

The website should have smooth scrolling for navigation and subtle interaction effects like button hover transitions. It must be lightweight, load quickly, and be fully responsive across all devices.
```

### 429 calling openai API
```
openai.RateLimitError: Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}
```

### openai is not defined
- NameError: name 'openai' is not defined. Did you mean: 'OpenAI'?
- bug: use "client.images.generate(""

### TypeError: 'ImagesResponse' object is not subscriptable
- File "/home/ec2-user/myapp/app.py", line 18, in generate_and_save_image
- bug: image_url = response['data'][0]['url']
  - should be: response.data[0].url


------------------------------------------------------------


## Step 5. Register DNS in GoDaddy and Route53
* Step 1: register domain in GoDaddy
* Step 2: Update DNS Settings in GoDaddy
  - update your domain's DNS records in GoDaddy to point to Route 53.
  - Log in to GoDaddy.
  - Find the domain you want to configure and click DNS or Manage DNS.
  - Change the Name Servers
  - Scroll down to the Nameservers section.
  - Select Custom and click Enter custom nameservers.
  - Go back to Route 53 console
  - locate the NS records (Name Servers) in Rout53 hosted zone
  - locate four name servers like ns-1234.awsdns-56.org (these are the name servers assigned by AWS for your domain).
  - Copy these four name server addresses into the Custom Nameservers fields in GoDaddy.
  - It may take some time for the DNS changes to propagate across the internet, typically anywhere from a few minutes to 48 hours.
* Step 3: Set Up A Record in Route 53
  - Create an A Record
  - Set the Record Name
  - Leave it blank for the root domain (e.g., example.com).
  - If you're configuring a subdomain like www, enter www as the record name.
  - For Record Type, select A – IPv4 address.
  - For Value, enter the public IP address of your EC2 instance.
  - Leave the TTL (Time To Live) as default (usually 300 seconds).
* Step 4. Set Up a Subdomain (e.g., www)
  - add a CNAME record.
  - Go to Route 53
  - In the Hosted Zone for your domain, click Create Record.
  - Choose CNAME – Canonical Name for the record type.
  - For Record Name, enter www.
  - For Value, enter example.com (without www).
* Step 5. update Nginx config
  - old config backup

```nginx
    server {
        listen       80;
        listen       [::]:80;
        server_name  _;
        root         /usr/share/nginx/html;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        error_page 404 /404.html;
        location = /404.html {
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
        }
    }

    server {
        listen 80;
        server_name <public-ip>;

        location / {
            proxy_pass http://127.0.0.1:8000;  # Forward requests to Gunicorn
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            root /home/ec2-user/myapp/app.py;
        }
    }
```

  - new config for http://adengbao.com/ and http://adengbao.com:8000

```nginx
    server {
        server_name adengbao.com www.adengbao.com;

        # Forward to Gunicorn
        location / {
            proxy_pass http://127.0.0.1:8000;  # Forward requests to Gunicorn
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /home/ec2-user/myapp/static/;
        }
    }
```

### NameServer
- translate human-readable domain names into IP addresses
- the web app is running on EC2 instance; Route53 is handling DNS queries => in order to route the DNS lookup to the correct IP address
- GoDaddy's default DNS does not know about the EC2 instance

### A record
- a DNS record that maps a domain name to IPv4 address
- by default, Route53 would have A Record for the hosted zone, value is EC2 instance's public IP

### SOA Record
- start of authority
- includes info about a domain's DNS zone, including primary NameServer, admin, etc
- by default, Route53 would have SOA record, value is "ns-869.awsdns-44.net. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"

### NS Record
When you create a hosted zone, Amazon Route 53 allocates a delegation set (a set of four name servers) to serve your hosted zone. Route 53 then creates a name server (NS) record inside the zone, with the same name as your hosted zone, that lists the four allocated name servers.
- record name = hosted zone name
- value = 4 name servers

### CNAME
- A DNS record that maps one domain name (alias) to another domain name.
- for subdomains to point them to a primary domain.

------------------------------------------------------------

## Step 6. setup SSL in Nginx using certbot
```commandline
sudo dnf install -y epel-release
sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d adengbao.com -d www.adengbao.com
```

* run certbot

```log
sudo certbot --nginx -d adengbao.com -d www.adengbao.com
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Enter email address (used for urgent renewal and security notices)
(Enter 'c' to cancel): <your email>
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.4-April-3-2024.pdf. 
You must agree in order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
(Y)es/(N)o: Y
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: N
Account registered.
Requesting a certificate for adengbao.com and www.adengbao.com
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/adengbao.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/adengbao.com/privkey.pem
This certificate expires on 2025-02-24.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.
Deploying certificate
Successfully deployed certificate for adengbao.com to /etc/nginx/nginx.conf
Successfully deployed certificate for www.adengbao.com to /etc/nginx/nginx.conf
Congratulations! You have successfully enabled HTTPS on https://adengbao.com and https://www.adengbao.com
```

* Configure Automatic SSL Renewal 
* verify Nginx config

```commandline
sudo nginx -t
sudo systemctl reload nginx
```

* nginx config
```nginx
    server {
        server_name adengbao.com www.adengbao.com;

        # Forward to Gunicorn
        location / {
            proxy_pass http://127.0.0.1:8000;  # Forward requests to Gunicorn
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /home/ec2-user/myapp/static/;
        }
        
        # following are added by Certbot, see next
        listen [::]:443 ssl ipv6only=on; # managed by Certbot
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/adengbao.com/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/adengbao.com/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
```

### bug: missing image

```log
Request URL:
https://adengbao.com/static/images/hero-image.jpg
Request Method:
GET
Status Code:
403 Forbidden (from service worker)


2024/11/26 02:05:50 [error] 8759#8759: *6 open() "/home/ec2-user/myapp/static/static/images/about-image.jpg" failed (13: Permission denied), client: <ip>, server: adengbao.com, request: "GET /static/images/about-image.jpg HTTP/1.1", host: "adengbao.com", referrer: "https://adengbao.com/"

=> solution:
sudo chown -R nginx:nginx /home/ec2-user/myapp/static
sudo chmod -R 755 /home/ec2-user/myapp/static
sudo chmod +x /home/ec2-user
sudo chmod +x /home/ec2-user/myapp
sudo chmod +x /home/ec2-user/myapp/static
sudo -u nginx ls /home/ec2-user/myapp/static/images/hero-image.jpg
sudo systemctl restart nginx
```

------------------------------------------------------------

## Step 7. publish website
- local zip
  - zip -r myapp-v3-20241126-llm-house-listing.zip ./myapp/ 
- upload zip
  - scp -i ~/cz-aws-default-key.pem /home/<user>/myapp-v3-20241126-llm-house-listing.zip ec2-user@ec2-...
- remote unzip
  - sudo chown -R ec2-user:ec2-user /home/ec2-user/myapp/static
  - unzip -o myapp-v3-20241126-llm-house-listing.zip
  - sudo chown -R nginx:nginx myapp/static/images
  - pkill gunicorn
  - gunicorn --workers 3 --bind 0.0.0.0:8000 myapp.app:app


------------------------------------------------------------


## Step 8. Design Synthetic Data Generation
- phase 1
  - onboard openai API
  - onboard HTTPS/SSL/DNS
- phase 2 - synthetic data gen
  - problem: how to simulate real users opening website
  - problem: how to simulate traffic from different regions in US, EU and China
  - problem: how to simulate traffic from different agents (mobile, website, ..)
  - problem: how to switch the website (input)
  - problem: how to rate limit (input)
  - problem: how to have human behavior and interactions

### High level idea:
1. use LLM to generate X user behavior patterns on a given website
2. use LLM to generate Y user profiles (agents, region) while browsing the website
3. given Y user profiles, and X user behavior patterns, use LLM to pick up one user interaction as (x, y) user_interactions_x_y.txt
4. given the interaction (x, y), and given the website html, generate Selenium-based code/script: user_interactions_x_y.py


### user interactions data
- website -> user behavior patterns X
- LLM -> user profiles Y 
- LLM + X + Y -> pick one -> interaction (x, y)


------------------------------------------------------------

## Step 9. Prompt template - generate synthetic user behavior data

```prompt
Given the following HTML structure, understand the topic of the website, its sections, images, paragraphs.
Generate a user behavior pattern based on the website content.
Must always include an explanation on how the behavior is generated.

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luxury Homes in Bellevue, Kirkland, and Redmond</title>
    <meta name="monetag" content="42c82687f7801605e0b2207e69360284">
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            scroll-behavior: smooth;
        }
        header {
            position: sticky;
            top: 0;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px 20px;
            z-index: 1000;
        }
        nav ul {
            list-style-type: none;
            padding: 0;
            display: flex;
            justify-content: space-around;
        }
        nav ul li a {
            color: white;
            text-decoration: none;
            padding: 10px;
            transition: color 0.3s;
        }
        nav ul li a:hover {
            color: #f0c040;
        }
        .hero {
            height: 100vh;
            background-image: url("/static/images/hero-image.jpg");
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            position: relative;
        }
        .hero::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
        }
        .hero h1 {
            z-index: 1;
            font-size: 3em;
            margin: 0;
        }
        .hero p {
            z-index: 1;
            font-size: 1.5em;
            opacity: 0;
            transform: translateY(20px);
            animation: slideIn 1s forwards;
            animation-delay: 0.5s;
        }
        @keyframes slideIn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .about, .listings, .contact {
            padding: 50px 20px;
            text-align: center;
        }
        .about img {
            width: 300px;
            transition: transform 0.3s;
        }
        .about img:hover {
            transform: scale(1.1);
        }
        .listing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .listing-item {
            position: relative;
            overflow: hidden;
            transition: transform 0.3s;
        }
        .listing-item img {
            width: 100%;
            display: block;
        }
        .listing-item p {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .listing-item:hover {
            transform: scale(1.05);
        }
        .listing-item:hover p {
            opacity: 1;
        }
        .contact {
            background: #f0f0f0;
        }
        .contact form {
            display: flex;
            flex-direction: column;
            max-width: 400px;
            margin: auto;
        }
        .contact input, .contact textarea {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .contact button {
            padding: 10px;
            background: #333;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .contact button:hover {
            background: #555;
        }
        footer {
            text-align: center;
            padding: 20px;
            background: #333;
            color: white;
            position: sticky;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#listings">Listings</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <section class="hero" id="home">
        <h1>Luxury Living Awaits</h1>
        <p>Discover your dream home in the heart of Bellevue, Kirkland, and Redmond.</p>
    </section>
    <section class="about" id="about">
        <h2>About Us</h2>
        <div style="display: flex; justify-content: center; align-items: center;">
            <img src="/static/images/about-image.jpg" alt="About Image">
            <div style="margin-left: 20px;">
                <p>We are dedicated to providing the best luxury real estate listings in the area.</p>
            </div>
        </div>
    </section>
    <section class="listings" id="listings">
        <h2>Listings</h2>
        <div class="listing-grid">
            <div class="listing-item">
                <img src="/static/images/listing-image-1.jpg" alt="Listing">
                <p>List item description here...</p>
            </div>
            <div class="listing-item">
                <img src="/static/images/listing-image-2.jpg" alt="Listing">
                <p>List item description here...</p>
            </div>
            <div class="listing-item">
                <img src="/static/images/listing-image-3.jpg" alt="Listing">
                <p>List item description here...</p>
            </div>
            <div class="listing-item">
                <img src="/static/images/listing-image-4.jpg" alt="Listing">
                <p>List item description here...</p>
            </div>
        </div>
    </section>
    <section class="contact" id="contact">
        <h2>Contact Us</h2>
        <form onsubmit="return validateForm()">
            <input type="text" id="name" placeholder="Your Name" required="">
            <input type="email" id="email" placeholder="Your Email" required="">
            <textarea id="message" placeholder="Your Message" required=""></textarea>
            <button type="submit">Submit</button>
        </form>
    </section>
    <footer>
        <p>© 2024 ADengBao BRK Homes. All rights reserved.</p>
    </footer>
    <script>
        function validateForm() {
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const message = document.getElementById('message').value;
            if (name && email && message) {
                alert('Form submitted successfully!');
                return true;
            }
            alert('Please fill out all fields.');
            return false;
        }
    </script>
</body>
</html>

Examples of user behavior pattern:
"User opens the website. They remain idle for 10 seconds, reading the page or glancing at the content. Afterward, they close the browser or navigate away without clicking anything."
"User opens the website. They begin scrolling slowly after 2 seconds, pausing occasionally as if reading. They stop scrolling at the midway point of the page (the 'About Us' section) and pause for 5 seconds before exiting."
"User opens the website. They begin scrolling slowly through the hero section and continue scrolling through the 'Listing' section, pausing for 3 seconds and clicks on one image. They then resume scrolling at a steady pace until they reach the footer. They stay on the footer for 7 seconds and exit."

Return in JSON format with following fields:
  "user_behavior_id": use 0 as integer,
  "user_behavior_description": use the generated behavior pattern.
  "explanation": the explanation on how the behavior is generated, based on the HTML tags.

User may not browse all sections.
User should not always click.
User should not always click an image.
User should not always click on the same element.
The output should always have an explanation.
The Explanation must specify tags of the HTML element, to make it traceable for Selenium.
If user clicks an img or url, the explanation must have the element's info, such as "listing-image-2.jpg".
Return example as pure JSON only, no formatting.

```

------------------------------------------------------------

## Appendix - Dev Logs
We have encountered/resolved the following problems:
1. long latency and high cost of generating >100 data points
2. generating json could have "..." or bad formatting (such as comments)
3. generate data in batches -> how to handle duplication across batches?


### problem: rate limit on calling openAI API
* Rate limit reached for gpt-4o-mini in organization on tokens per min (TPM): Limit 200000, Used 199403, Requested 15173. Please try again in 4.372s 
* option 1: max_concurrency=3
* option 2: token-based throttling


### problem: chrome driver
https://googlechromelabs.github.io/chrome-for-testing/
https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/linux64/chromedriver-linux64.zip


### run Selenium script after installing chrome
1. install chrome only
2. `run google-chrome --disable-gpu --disable-software-rasterizer --no-sandbox --disable-extensions --no-proxy-server --remote-debugging-port=9222 https://adengbao.com`
3. run Selenium script

### problem: why click on page was intercepted!?
```log
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <img src="/static/images/listing-image-2.jpg" alt="Listing"> is not clickable at point (692, 853). Other element would receive the click: <div style="border: none; position: absolute; top: 1271px; left: 0px; width: 705px; height: 1709px; z-index: 2147483647; pointer-events: auto;"></div>
  (Session info: chrome=131.0.6778.85)
Stacktrace:
Array.from(document.querySelectorAll("span")).find(el => el.textContent.trim() === "×");
Array.from(document.querySelectorAll("span")).find(el => el.textContent.trim() === "Close");
return document.querySelector("svg path");
```

* option 1:

```javascript
driver.execute_script("""
    var iframes = document.querySelectorAll('iframe');
    iframes.forEach(function(iframe) {
        iframe.parentNode.removeChild(iframe);
    });
""")
```

* option 2:
  * Message: element click intercepted: Element <img src="/static/images/listing-image-2.jpg" alt="Listing"> is not clickable at point (571, 645). Other element would receive the click: <iframe style="width: 100% !important; height: 100% !important; opacity: 1 !important; max-width: 100% !important; border: 0px !important; position: fixed !important; display: block !important; z-index: 2147483647 !important; inset: 0px 0px auto auto !important; background: rgba(0, 0, 0, 0.3) !important; color-scheme: auto !important; min-height: 100% !important; visibility: visible;"></iframe>
  * => close_div = driver.find_element(By.XPATH, "//span[text()='Close']/ancestor::div")

### problem: aggregate all scripts and execute on cloud
1. aggregate all cities by regions
2. aggregate all scripts by region
region 1 => [BRK] => [1,2,3]
region 2 => [Shanghai, Beijing] => [4,5,6]
3. launch instances per region
4. for each region, loop each associated interaction id, locate the corresponding interaction script, also locate its user_agent from JSON
5. for a given interaction script, execute it with user_agent
6. log exit code









