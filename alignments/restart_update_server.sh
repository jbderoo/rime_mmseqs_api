sudo systemctl daemon-reload
sudo systemctl restart flask_app.service
sudo systemctl status flask_app.service

# What does good output look like?
#  
# ### Start Output ###
#  ● flask_app.service - MMSEQS@Flask Alignment App
#       Loaded: loaded (/etc/systemd/system/flask_app.service; enabled; vendor preset: enabled)
#       Active: active (running) since Wed 2024-09-04 23:03:27 MDT; 23ms ago
#     Main PID: 183686 (bash)
#        Tasks: 3 (limit: 629145)
#       Memory: 5.4M
#          CPU: 17ms
#       CGroup: /system.slice/flask_app.service
#               ├─183686 /bin/bash -c "source /home/csnow/miniforge3/etc/profile.d/conda.sh && conda activat>
#               ├─183691 /bin/bash -c "source /home/csnow/miniforge3/etc/profile.d/conda.sh && conda activat>
#               └─183692 /home/csnow/miniforge3/bin/python /home/csnow/miniforge3/bin/conda shell.posix acti>
#  
#  Sep 04 23:03:27 rime systemd[1]: Started MMSEQS@Flask Alignment App.
#
# ### End Output ###
#
# The dot on the first line, to the left of `flask_app.service`, is green for me
# The third line, the `active (running)` to the right of `Active:` is green for me 
# Push 'q' to exit the status update message thing
