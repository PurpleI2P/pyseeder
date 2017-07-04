Installation
============

Requirements: python3 and python cryptography package, requests for transports


Example for Ubuntu/Debian
-------------------------


Basic python packages & packages for building python cryptography package:

    sudo apt-get install python3 python3-pip python3-virtualenv build-essential libssl-dev libffi-dev python-dev


Clone repo:

    git clone https://github.com/PurpleI2P/pyseeder.git


Configure new python virtual environment:

    cd pyseeder
    virtualenv --python=python3 venv
    . venv/bin/activate
    pip3 install .


Thats it! Next time you will need to run pyseeder, don't forget to activate 
python virtual environment as followed:

    . venv/bin/activate

