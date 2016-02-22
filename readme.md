# HLS BBA testbed

![Topology](topology.png)

## Warning
* NEVER never never run multiple instances of `vagrant up` in parallel: machines will mix and everything will break.


## Dependencies
* [VirtualBox](https://www.virtualbox.org/) 4.3
* [Vagrant](https://www.vagrantup.com/) 1.8.1
* Python 2.7.8: if this is not your default version, you can install [pyenv](https://github.com/yyuu/pyenv) and run `pyenv install 2.7.8`.
* matplotlib 1.3.1 and scipy 0.14.0:
  * if you're using system-wide Python in Ubuntu: `apt-get install python-matplotlib python-scipy`
  * if not: `pip install -r requirements.txt` (Ubuntu packages you'll probably need: python-pip pkg-config python-dev libfreetype6-dev libpng12-dev)
* tcptrace 6.6.7, tshark 1.10.6: to plot `iperf` sessions
* GNU parallel (>20130522)
Other versions could work.


## Install
* First, install dependencies.
* Clone this repository and our customized version of [VLC media player](https://github.com/serl/vlc): `git clone https://github.com/serl/hls-bba-testbed.git && cd hls-bba-testbed && git submodule update --init`.
* The testbed comes without videos; in order to get the same version of Big Buck Bunny that we used (~800MB), run: `wget https://s3-eu-west-1.amazonaws.com/hls-bba-testbed/bbb8.tar.gz && tar -C code/http_server/static -xzf bbb8.tar.gz && rm bbb8.tar.gz`. Clients will have access through the bottleneck to whatever is in the `code/http_server/static` folder.
* Create and configure the machines: `vagrant up && vagrant up client0 client1 client2`. It will also compile VLC. This will take approximately 30 minutes and 5 GB of disk space. Machines are configured to get at most 2GB of RAM each (so 12GB in total).


## Everyday use

### Running the tests
* Populate the `tests` directory by running `python vlc_test.py`.
* Run one or more tests (in sequence) with `./run_schedule.sh [N] <session_dir> [session_dir...]`, where `N` is optional and represents the number of runs you want for each test (default `1`) and `session_dir` is the directory containing a file named `jobs.sched` (for example `tests/constant_1_bbb8_80ms_100%BDP_droptail/c01_1_bbb8_600kbit_bba3_keepalive_est`). A shortcut to run all tests is `./run_schedule.sh tests/*/*/`, but beware: it will take about 25 days.
* The results for each run of each test will be stored in `session_dir/N.tar.gz`, for example `tests/constant_1_bbb8_80ms_100%BDP_droptail/c01_1_bbb8_600kbit_bba3_keepalive_est/1.tar.gz`.
* Right after each run, a *post\_run* routine will be launched, analyzing dropped packets and generating a plot about the test. In our example the image path will be `tests/constant_1_bbb8_80ms_100%BDP_droptail/c01_1_bbb8_600kbit_bba3_keepalive_est_1.png`.

### Analyzing the results
* A zoomable plot could be obtained by running `./plot_display.sh <rundir>`, where `rundir` is the path to a `.tar.gz` file: this will open the matplotlib graphical interface.
* `./check_tests.sh tests/` will tell you if and which runs are missing.
* `./analyze_vlc_QoE.sh tests/` will calculate the averages for some metrics and create some useful csv files:
  * `tests/QoE_metrics/summary.csv` by averaging on all the constant-bandwidth bottlenecks
  * `tests/QoE_metrics_variable/v0(1|2)_summary.csv` by averaging separately on the two variable-bandwidth bottleneck profiles (with fair shares of *4Mbit-1Mbit-4Mbit-600kbit-4Mbit* and *4Mbit-2.8Mbit-1.5Mbit-1Mbit-600kbit-4Mbit*).


## Tips and tricks
* In order to have a comprehensive plot of multi-client runs: `python plot_vlc_compare_runs.py [export] <session_dir(s)>` (and not `run_dir`!). It will generate a plot with the bit rate requested and the bandwidth fair share, taking all the clients and all the runs. If more than one `session_dir` is asked for, images in png format will be exported in `session_dir`, otherwise an interactive plot will open (the export behavior can be forced by giving the optional `export` argument).
* You can easily run `iperf` by generating tests crafted for it: `python iperf_test.py` (take a look at the Python script to see or modify the parameters); after each test, plots will be automatically generated; for interactive plots, you can run `./plot_display.sh <rundir>` as usually.
* Update the testbed to the latest version: `./update.sh`. It will resync to the repositories and, if wanted, recompile VLC.
* Receive an email at the end of the execution of the tests: create a file named `.mail` with an email address; it relies on the `mail` command.
* Avoid halting all virtual machines after a batch of tests: create an empty file named `.noreload`.
* Rerun *post\_run* routine (calculating dropped packets and generating png plots): `./rerun_post_run.sh <rundirs...>`.
* Recompile VLC: `vagrant up client0 && vagrant ssh client0 -c 'bash /vagrant/scripts/compile_vlc.sh update'`.
* Run more than three clients and/or change the amount of RAM/CPUs: change the respective values in `Vagrantfile`, then configure the new machines by running `vagrant up clientN clientN-1...` or reconfigure old machines by halting them with `vagrant halt` (the new values will be active at boot).
* You could exploit Python on a virtual machine (not recommended), use `./python.sh`, and everything should (slowly) work out of the box.
* You can decompress/recompress individual or a group of runs by running `./(de)compress.sh <rundir(s)>`. Un-compressed runs will work as well as compressed ones with (hopefully) all tools.
* Run tests with another video: make sure it is in Apple HLS format, and put it into `code/http_server/static` folder. In order to make BBA-1+ work properly, you need to modify the HLS *sub-*playlists to include the segment sizes, by running `python hls-size-helper.py <path/to/subplaylist.m3u8> > <path/to/subplaylist_size.m3u8>`; then modify (or copy) the *master* playlist to point to the new sub-playlists.


## To be fixed
* `plot_vlc_scatters.sh` was designed to generate (but does not work at the moment) scatterplots similar to the ones you can find in Akhshabi, Saamer, et al. "What happens when HTTP adaptive streaming players compete for bandwidth?" *Proceedings of the 22nd international workshop on Network and Operating System Support for Digital Audio and Video.* ACM, 2012.
* `compare_sessions.py` was designed to compare the bit rates obtained by different families with a bar graph; it is not maintained and probably not working anymore.
