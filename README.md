# UK Polling Stations build and deploy

## Setup

- `pipenv install`
- `ansible-galaxy install -r requirements.yml`
- Ensure your AWS credentials are in `~/.aws/credentials`
- `cp packer-user-vars.example.json packer-user-vars.json` and fill in the path to your private key file
- create `.vault_pass.txt` with your vault password

## Amazon Machine Images (AMI)

We use [packer](https://www.packer.io/) to build golden AMIS.
On OSX this can be installed via `brew install packer`.
The AMIs we build are designed to come up as quickly as
possible so they can serve traffic. This means that they contain the entire
AddressBase db pre-imported. To make import script-only or code-only changes
quicker we have three AMIS:

- The `addressbase` AMI which just has postgres with AddressBase imported
- The `imported-db` AMI which is built off the `addressbase` AMI and also has
  the import scripts run against it.
- The `server` AMI which is built off the `imported-db` AMI and also contains
  the code/app.

This makes the build process much faster if we want to deploy code-only updates.
Each image is described as a `builders` object in `packer.json`.


### How to build

If the there is a new AddressBase release release,
or if you haven't built it yet then:

#### 1. Fetch latest AddressBase

- Order a new copy from the OS website and download it from their FTP
- The files will be in a directory named something like DCS0000000000
- Upload the files to
  s3://pollingstations-packer-assets/addressbase/DCS0000000000
- Replace `addressbase_folder_name` in `vars.yml` with the directory name
  (e.g: DCS0000000000)

#### 2. Make the image

- If you need to build the `addressbase image` run:

        AWS_PROFILE=democlub ./packer addressbase

  That will output an AMI id that you will need to manually copy. Look for
  lines like this near the end of the output:

      ==> database: Creating the AMI: addressbase 2016-06-20T12-38-27Z
          database: AMI: ami-7c8f160f

  (This might take a *long* time at the "Waiting for AMI to become ready..."
  stage)

  The AMI id (`ami-7c8f160f` in this case) needs to go into
  `./packer-vars.json` in the `database_ami_id` key.

- If the pollingstations/council dump has changed then similary to
  `addressbase` above run

        AWS_PROFILE=democlub ./packer imported-db

  and store the resulting AMI id in the `imported-db_ami_id` key in
  `./packer-vars.json`.

  This will build one the addressbase AMI and include in the councils and
  polling stations data.

- To make just a code change, build the `server` AMI. This is built on the
  `imported-db` AMI and just adds the code changes.

        AWS_PROFILE=democlub ./packer server

  **NOTE**: To run this you will need the Ansible Vault password. Place it in
  a `.vault_pass.txt` file in the same directory as this file. To view the
  vault variables run `ansible-vault view vault.yml`.

- To deploy the image we've built:
  - Update `aws.yml`:
    - Set `ami_id` to image ID from last packer run (e.g: `ami-2bbe8e4d`)
    - Find the `lc_num` value of the previous instance we deployed and set
      `lc_num` to (previous `lc_num` + 1). This can be found by looking at the
      Launch Configuration names in the AWS console.
      When we deploy, this will clean up the previous image.
    - Set `desired_capacity` to a sensible number under
      "On-demand Autoscailing group" (e.g: 4 for peak times, 1 for off-peak).
      Note we use "On-demand Autoscailing group" for live/staging instances,
      "Spot price Autoscailing group" is used for building images so
      `desired_capacity` should be 1 for "Spot price Autoscailing group".
  - If we're deploying to production, `export ENVIRONMENT=prod`. Obviously
    don't do this if it is a staging deploy!
  - Run

        AWS_PROFILE=democlub ansible-playbook aws.yml -e replace_all=True

  This will create a new launch config, associated the ASG with it, and then
  delete the old one. If `replace_all` is set then it will also cycle all the
  old instances (1 by 1) to make them use new ones.
  - To test a staging deploy, ensure `stage.wheredoivote.co.uk` is pointed at
    the staging load balancer.
  - Once you've tested a staging build, the cleanest way to decommission the
    staging instance is to set the desired and minimum number of instances on
    the `pollingstations-asg-test` ASG to zero.

### Debugging the build

If something is going wrong with the ansible or other commands you run on the
build then the best tool for debugging it is to SSH onto the instance. By
default packer will terminate the instance as soon as it errors though. If you
add `-debug` (note: **one** dash) flag then packer will pause at each stage
until you hit enter, giving you the time to SSH in and examine the server.

Packer will generate a per-build SSH private key which you will have to use:

    ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  \
      -l ubuntu -i ./ec2_server.pem 54.229.202.43

(The IP address will change every time too - get that from the output.)

## Ad-hoc tasks

Sometimes you need to fix something urgently and you don't want to wait for an
AMI rebuild. In which case you can use the ansible dynamic inventory:

    ANSIBLE_HOST_KEY_CHECKING=False AWS_PROFILE=democlub \
    ansible -i dynamic-inventory/ \
      -b --become-user polling_stations \
      tag_Env_prod \
      -a id

The above command will run `id` as the polling_stations user. This invokes the
[command module][ansible_command_module] - you might want to add `-a shell` if
your command is more complex.

What ever change you make don't forget to roll it back into the AMI, create a
new launch config and update the ASG config (even if you don't replace the
existing instances) otherwise a scaling event or failed host will "revert"
your changes.

[ansible_command_module]: http://docs.ansible.com/ansible/command_module.html

### Ad-hoc deploy

`ansible-playbook -u myusername -i dynamic-inventory/ -l tag_Env_prod deploy.yml --extra-vars @vault.yml`

### Take down data

`ansible -u myusername -i dynamic-inventory/ -b --become-user polling_stations tag_Env_prod -m shell -a  "cd /var/www/polling_stations/code/ && ../env/bin/python manage.py teardown -c X01000001"`
