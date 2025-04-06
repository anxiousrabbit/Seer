
# Seer

Seer is the companion application for Weaver and is the attacker console for the command and control channel. Included in this packages is the Python code for the console itself as well as the Terraform code for the infrastructure that is hosted in AWS. The AWS infrastructure looks like this:
![Architecture diagram](assets/seerInfrastructure)

## Installation

Prior to installing seeing, make sure the most recent version of Python3 is installed and Terrform is installed. Along with that, make sure that you have an AWS account created and configured so Terraform can access the account for its infrastructure creation.

```bash
pip3 install -r requirements.txt
cd terraform
terraform plan
```

Validate Terraforms output and then run:
```bash
terraform apply
```

#### When running terraform plan:
- Enter the name of the s3 bucket you want to generate.
- The output will return the domain that your API Gateways will be accessible from. You will need this for the `variables.swift` file for Weaver.
- An API key is also generated. Terraform does not output plaintext secrets, this will need to be retrieved from the AWS console. Once retrieved, you will use that in the `variables.swift` file for Weaver.

Once the infrastructure is created, Seer can be ran.
 
## Features
```
-h, --help     show this help message and exit
-p P           Sets the PSM level. The default is 11
-d             Enables retrieving data from dynamo
-de            Deletes the entry within dynamodb
-l             Lists the hosts in the s3 bucket
-o             Output the images received from the compromised host
--commImage    Outputs the command image
-b B           Sets the bucket to pull data from
--init         Initialize the config file
--reinit       Reinitializes the config file
--reUpload     Reuploads images to the s3 bucket
--dalleUpdate  Updates the key used for Dalle
```

BUG: The Dalle integration hasn't been touched in a while and might not function as expected
## Usage/Examples
NOTE: these examples assume you are running Python in a virtual environment.

#### Initial Seer. RUN THIS FIRST
```python
python3 -m seer --init
```
#### List hosts that have been compromised
```python
python3 -m seer -l
```
#### List compromised hosts and output the images from the compromised host
```python
python3 -m seer -l -o
```
#### Send commands to a hostname you already know
```python
python3 -m seer -b <hostname>
```
