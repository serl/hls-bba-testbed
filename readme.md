# HLS BBA testbed

Documentation in progress...


## Dependancies

### Testing
* Vagrant and VirtualBox
* video files in `code/http\_server/static`

### Analysis
To exploit the already configured python on a virtual machine, use `./python.sh`, and everything should (slowly) work out of the box. Otherwhise, you can use your own python.
This configuration should ensure everything is working:

* python (2.7.8) pyenv install 2.7.8
* matplotlib (1.4.3) pip install -r requirements.txt (Ubuntu packages you'll need: python-pip pkg-config python-dev libfreetype6-dev libpng12-dev)
* tcptrace (6.6.7), tshark (1.10.6) to use plot_iperf.py
* GNU parallel (>20130522)


## How to
* rerun post\_run analysis: `vagrant ssh server`, `/vagrant/code/post\_run.sh <rundirs...>`. Where each `rundir` is in the form `/vagrant/tests/...`

