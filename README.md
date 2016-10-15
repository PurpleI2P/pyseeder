pyseeder
========

Reseed data managment tools for I2P

* Generate reseed signing keypair
* Make reseed data files (su3)
* Download su3 files from official servers for mirroring
* Upload reseed data to different places (with plugins)
* Run HTTPS reseed server

Reseed transports are implemented so that users can bootstrap their I2P nodes
without needing to connect to "official" I2P reseeds. This makes I2P more
invisible for firewalls.

[Installation instructions](INSTALL.md)


Usage
-----

    $ python3 pyseeder.py --help
    $ python3 pyseeder.py keygen --help


Generating keypair
------------------


    $ python3 pyseeder.py keygen --cert data/user_at_mail.i2p.crt --private-key data/priv_key.pem --signer-id user@mail.i2p

This will generate certificate (user\_at\_mail.i2p.crt) and private RSA key
(priv\_key.pem) in data folder. E-mail is used as certificate identifier.

Script will prompt for private key password.


Generating reseed data
----------------------


    $ YOUR_PASSWORD="Pa55w0rd"
    $ echo $YOUR_PASSWORD | python3 pyseeder.py reseed --netdb /path/to/netDb --private-key data/priv_key.pem --outfile output/i2pseeds.su3 --signer-id user@mail.i2p

This will generate file i2pseeds.su3 in output folder, using user@mail.i2p as
certificate identifier.

Note:  you'll have to enter your private key password to stdin, the above
is one of the ways to do it (for cron and scripts).


Download su3 file from official servers
---------------------------------------

    $ python3 pyseeder.py transport.pull --urls https://reseed.i2p-projekt.de/ https://reseed.i2p.vzaws.com:8443/ --outfile output/i2pseeds.su3

Note: --urls parameter is optional, defaults are "official" I2P reseeds.


Upload su3 file with pluggable transports
-----------------------------------------

    $ python3 pyseeder.py transport.push --config transports.ini --file output/i2pseeds.su3

All parameters are optional. Copy file transports.ini.example to 
transports.ini. Edit your settings in this new file.


Run HTTPS reseed server
-----------------------

    $ python3 pyseeder.py serve --port 8443 --host 127.0.0.1 --private-key data/priv_key.pem --cert data/user_at_mail.i2p.crt --file output/i2pseeds.su3

Note: this server is fine for testing, but for "production" environments please
use nginx webserver.
