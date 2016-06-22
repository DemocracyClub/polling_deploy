# UK Polling Stations build and deploy

## Amazon Machine Images (AMI)

We user [packer] to build golden AMIS. On OSX this can be installed via `brew
install packer`. The AMIs we build are designed to come up as quickly as
possible os they can serve traffic. This means that they contain the entier
AddressBase db pre-imported. To make code-only changes quicker we have two
amis.

- The "imported DB" ami which has postgres and the DB imported but nothing
  else.
- The code/app AMI which is built off the DB ami. This is much faster to build
  as we don't have to wait for the multi gigabyte Postgres dump to restore.


### How to build

- If the addressbase dump has changed, or if you haven't built it yet then:

        AWS_PROFILE=democlub ./packer addressbase

  That will output an AMI id that you will need to manually copy. Look for
  lines like this near the end of the output:

      ==> database: Creating the AMI: addressbase 2016-06-20T12-38-27Z
          database: AMI: ami-7c8f160f

  (This might take a *long* time at the "Waiting for AMI to become ready..."
  stage)

  The AMI id (`ami-7c8f160f` in this case) needs to go into
  `./packer-vars.json` under the database_ami_id.

- If the pollingstations/council dump has changed then similary to
    `addressbase` above run

        AWS_PROFILE=democlub ./packer imported-db

  and store the resulting AMI id in the `imported-db_ami_id` key.

  This will build one the addressbase AMI and include in the councils and
  polling stations data.

- To make just a code change the build the `server` AMI. This is built on the
    `imported-db` AMI and just adds the code changes.

        ./packer server

  **NOTE**: To run this you will need the Ansible Vault password. Place it in
  a `.vault_pass.txt` file in the same directory as this file.

### Debugging the build

If something is going wrong with the ansible or other commands you run on the
build then the best tool for debugging it is to SSH onto the instance. By
default packer will terminate the instance as soon as it errors though. If you
add `-debug` flag then packer will pause at each stage until you hit enter,
giving you the time to SSH in and examine the server.

Packer will generate a per-build SSH private key which you will have to use:

    ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  \
      -l ubuntu -i ./ec2_server.pem 54.229.202.43

(The IP address will change every time too - get that from the output.)


[packer]: https://www.packer.io/
