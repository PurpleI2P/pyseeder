Pyseeder docker container
=========================

Using it with i2pd container:

1) Run i2pd docker container and locate it's datadir volume with `docker inspect <container>`

   It will show something like that:

        ...

        "Mounts": [
            {
                "Name": "69c5fb747b09701acebcf22478f99719e87ac65b3ac11464cd949bebe03a744a",
                "Source": "/var/lib/docker/volumes/69c5fb747b09701acebcf22478f99719e87ac65b3ac11464cd949bebe03a744a/_data",
                "Destination": "/home/i2pd/data",
                "Driver": "local",
                "Mode": "",
                "RW": true,
                "Propagation": ""
            }
        ],

        ...

2) Run pyseeder image with that volume mounted at `/i2pd_data`:

    docker run --name=test10 -P -dt -v 69c5fb747b09701acebcf22478f99719e87ac65b3ac11464cd949bebe03a744a:/i2pd_data pyseeder

3) Enjoy your reseed.
