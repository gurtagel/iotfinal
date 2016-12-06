import os
import RPi.GPIO as GPIO, time
import subprocess
import re
import socket
from flask import Flask
app = Flask(__name__)


#change these variables depending on your own configuration
sound_gpio_port = 17
slave_hostname = "pi"
slave_ip_addr = "192.168.1.111"
master_temp_gpio_port = 4
slave_temp_gpio_port = 2
master_adafruit_loc = "../Adafruit_Python_DHT/examples/AdafruitDHT.py"
slave_adafruit_loc = "Adafruit_Python_DHT/examples/AdafruitDHT.py"

@app.route("/")
def hello():
    #getting values from sound sensor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sound_gpio_port, GPIO.IN)
    loud_list = []
    switch = 0
    for i in range(1000):
        loud_list.append(GPIO.input(sound_gpio_port))
    for i in range(1000):
        if loud_list[i] > 0:
            switch = 1
    if switch > 0:
        loudness = "loud"
    else:
        loudness = "quiet"
    

    #here we are creating the html header for the webserver
    x= """<!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="30" >
    <title>Computer Science Lab</title>
    <style>
    input[type=text] {
    padding: 0;
    height: 30px;
    position: relative;
    left: 0;
    outline: none;
    border: 1px solid #cdcdcd;
    border-color: rgba(0,0,0,.15);
    background-color: white;
    font-size: 16px;
    margin-left: 20px;
    }
    .search {
    width: 526px;
    margin-right: -4px;
    }
    </style>
    <!-- jQuery -->
<script src="https://mottie.github.io/tablesorter/docs/js/jquery-latest.min.js">
    </script>
    <!-- Demo stuff -->
<link rel="stylesheet"
href="https://mottie.github.io/tablesorter/docs/css/jq.css">
    <!-- Tablesorter: required -->
    <link rel="stylesheet"
    href="https://mottie.github.io/tablesorter/css/theme.blue.css">
<script src="https://mottie.github.io/tablesorter/js/jquery.tablesorter.js">
</script>
<script src="https://mottie.github.io/tablesorter/js/widgets/widget-filter.js">
</script>
<script id="js">
$(function() {
var $table = $("table").tablesorter({
theme: "blue",
widgets: ["zebra", "filter"],
widgetOptions : {
filter_external : ".search",
filter_defaultFilter: { 1 : "~{query}" },
filter_columnFilters: false,
filter_placeholder: { search : "Search..." },
filter_saveFilters : true,
filter_reset: ".reset"
}
});
$("button[data-column]").on("click", function(){
var $this = $(this),
totalColumns = $table[0].config.columns,
col = $this.data("column"),
filter = [];
filter[ col === "all" ? totalColumns : col ] = $this.text();
$table.trigger("search", [ filter ]);
return false;
});
});
</script>
</head>
<body>
<p>
<b>Computer Science Lab</b>
<br>
<br>
<b>Sensor 1</b>
<table id="myTable" class="tablesorter">
<thead>
<tr>
<th>Temperature</th>
<th>Humidity</th>
<th>Sound Level</th>
</tr>
</thead>
<tbody>"""

    degree_sign= u'\N{DEGREE SIGN}'
    parser = subprocess.check_output(master_adafruit_loc + " 11 " + str(master_temp_gpio_port)  + "", shell=True).strip('\n').split(' ')
    temp = re.findall("\d+\.\d+", parser[0])[0]
    humd = re.findall("\d+\.\d+", parser[2])[0]
    # Add what needs to be done to add sound here
    x += ("<tr>\n<td>" + temp + degree_sign + " F</td>\n<td>" + humd + "%</td>\n<td>" + loudness + "</td>\n</tr>\n")
    x += "</tbody>\n</table>\n"
    x += "<br>\n<br>\n<br>\n<br>\n<br>\n<b>Sensor 2</b>\n"
    x += """<table id="myTable" class="tablesorter">\n<thead>\n<tr>\n<th>Temperature</th>\n<th>Humidity</th>\n</tr>\n</thead>\n<tbody>\n"""
    
    #Add logic here to get data from remote sensor
    ssh_data = subprocess.check_output("ssh " + slave_hostname  + "@" + slave_ip_addr + " '" + slave_adafruit_loc  + " 11 " + str(slave_temp_gpio_port)  + "'", shell=True).strip('\n')
    parser = ssh_data.split(' ')
    temp2 = re.findall("\d+\.\d+", parser[0])[0]
    humd2 = re.findall("\d+\.\d+", parser[2])[0]
    #END OF CHANGE
    x += ("<tr>\n<td>" + temp2 + degree_sign + " F</td>\n<td>" + humd2 + "%</td>\n</tr>\n")
    x += "</tbody>\n</table>\n"


    #Here we are combining the data from all sensors in the CSL into one statistic for temperature, humidity, and sound
    x += "<br>\n<br>\n<br>\n<br>\n<br>\n<b>Combined</b>\n"
    x += """<table id="myTable" class="tablesorter">\n<thead>\n<tr>\n<th>Temperature</th>\n<th>Humidity</th>\n<th>Temperature</th>\n</tr>\n</thead>\n<tbody>\n"""
    
    temp_comb = (float(temp) + float (temp2)) / 2.0
    humd_comb = (float(humd) + float (humd2)) / 2.0
    x += ("<tr>\n<td>" + str(temp_comb) + degree_sign + " F</td>\n<td>" + str(humd_comb) + "%</td>\n<td>" + str(loudness) + "</td>\n</tr>\n")
    x += "</tbody>\n</table>\n"
    x += "</body>\n</html>\n"
    return x

#run app on machine's own ip

if __name__ == "__main__":
    app.run(host= '0.0.0.0')


