import csv

from scipy import signal

import numpy as np
from bokeh.layouts import column
from bokeh.models import Div, TeX, LinearAxis, Range1d, HoverTool
from bokeh.plotting import figure, show

import datetime


div1 = Div(
    text=r"""
<h1> PH-COP climb test flight report</h1>
<h2>Aircraft</h2>
Tobago TB-10<br>
serial number: 2113<br>
Registration: PH-COP

<h2>Environment</h2>

QNH: 1018<br>
Temperature: 18C<br>
<br>
Denisty altitude: 330ft<br>

<h2>M&B</h2>
Measurement Done at MTOW<br>
<ul> 
    <li>Fuel ~ 34g</li>
    <li>Pilot 1 95 kg</li>
    <li>Pilot 2 80 kg</li>
    <li>Passenger: 72</li>
    <li>Cargo: 30 kg </li>
    </ul>
<p />

<h2>Data source</h2>
<p>
    GPS Data recorded with Sentry GPS<br>
</p>


<h2> Flight path</h2>
Take EHEH off runway 21<br>
Level at 1000ft on the way to OSCAR<br>
climb to 3000ft from OSCAR to TANGO<br>
Level off at 3000ft on norhtern heading until clear of EHEH TMA 4<br>
Climb to 8000 ft<br>
<br>
<a href="https://flightaware.com/live/flight/PHCOP/history/20220522/0824Z/EHEH/EHEH">Flight aware</a><br>
<br>

<iframe src="https://www.google.com/maps/d/embed?mid=1TF8wkvUMiLwczmBPZdn55YASHD5-UjU&ehbc=2E312F" width="640" height="480"></iframe>    

<h2>Climb performance</h2>
<h3>Raw data</h3>
"""
)

text2 = """
<p> Ground speed is represented to be able to diferentiate the period of the climb where the 
aircraft is trading airspeed for altitude and when the climb is established. 
</p>

<h2>Performance discrepancy</h2>

<table>
  <tr>
    <th>Density Altityde (ft)</th>
    <th>Measured (ft)</th>
    <th>POH (ft)</th>
    <th>discrepancy (%)</th>
  </tr>
  <tr>
    <td>0</td>
    <td>{}</td>
    <td>{}</td>
    <td>{:.2f}</td>
  </tr>
  <tr>
    <td>2000</td>
    <td>{}</td>
    <td>{}</td>
    <td>{:.2f}</td>
  </tr>
  <tr>
    <td>4000</td>
    <td>{}</td>
    <td>{}</td>
    <td>{:.2f}</td>
  </tr>
  <tr>
    <td>6000</td>
    <td>{}</td>
    <td>{}</td>
    <td>{:.2f}</td>
  </tr>
  <tr>
    <td>8000</td>
    <td>{}</td>
    <td>{}</td>
    <td>{:.2f}</td>
  </tr>
</table>

<h2>Conclusion</h2>

<p>
The discrepency in climb performance seems to be more prononced at lower altitude. 
</p>

<p>
The higher discrepency at 2000ft is probably to a combination of incorrect IAS (close to 75k) and incorrect
power setting. 
</p>

<p>
Overall the decrease in climb performance is probably an average around 10%.
</p>


"""


def Average(l):
    avg = sum(l) / len(l)
    return int(avg)


def makeGraph(imputData):

    fpm = []
    alt = []
    ts = []
    gs = []
    dt = []

    for line in imputData:
        dt.append(line[10])
        gs.append(float(line[5]))
        fpm.append(line[11])
        alt.append(line[3])
        ts.append(datetime.datetime.fromtimestamp(float(line[0])))

    N = 45
    fpmFilt = np.convolve(fpm, np.ones(N) / N, mode="valid")
    gsFilt = np.convolve(gs, np.ones(N) / N, mode="valid")

    poh = [657, 554, 449, 347, 255]
    avg = [
        Average(fpmFilt[13:61]),
        Average(fpmFilt[246:462]),
        Average(fpmFilt[590:844]),
        Average(fpmFilt[1008:1252]),
        Average(fpmFilt[1252:1525]),
    ]

    discrepenciesTable = []
    for i in range(5):
        discrepenciesTable.append(avg[i])
        discrepenciesTable.append(poh[i])
        discrepenciesTable.append((avg[i] / poh[i] - 1) * 100)

    p2 = figure(
        width=670,
        height=400,
        toolbar_location=None,
        y_range=(-1000, 2000),
        title="PH-COP climb perofrmance 2022-05-22",
        x_axis_type="datetime",
        tools=[HoverTool()],
    )

    p2.xaxis.axis_label = "Time"
    p2.yaxis.axis_label = "climb rate(fpm)"

    p2.line(
        ts[N - 1 :],
        fpmFilt,
        line_width=2,
        legend_label="GPS climb rate  ({}s sliding window average)".format(N),
    )

    p2.extra_y_ranges = {
        "alt": Range1d(start=-100, end=8500),
        "gs": Range1d(start=0, end=120),
    }
    p2.add_layout(LinearAxis(y_range_name="alt"), "right")
    p2.line(
        ts[N - 1 :],
        alt[N - 1 :],
        color="red",
        y_range_name="alt",
        legend_label="Altitude",
    )

    p2.add_layout(LinearAxis(y_range_name="gs"), "right")
    p2.line(
        ts[N - 1 :],
        gsFilt,
        color="green",
        y_range_name="gs",
        legend_label="Ground speed",
    )

    p2.legend.location = "bottom_right"

    p3 = figure(
        width=670,
        height=400,
        toolbar_location=None,
        title="PH-COP climb perofrmance 2022-05-22",
        x_axis_type="datetime",
        tools=[HoverTool()],
    )

    p3.xaxis.axis_label = "Time"
    p3.yaxis.axis_label = "Delta time"

    p3.line(
        ts,
        dt,
        line_width=2,
        legend_label="delta time".format(N),
    )

    div2 = Div(text=text2.format(*discrepenciesTable))
    # show(column(div1, p, div2))
    show(column(div1, p2, div2))


with open(
    "tracklog-E3D3CB68-039F-4D91-89FB-E1F1B8C8CE1B_cropped.csv", newline=""
) as csvfile:
    readerdata = csv.reader(csvfile, delimiter=",", quotechar="|")

    rawdata = list(readerdata)


rawdata = rawdata[3:]
computedData = []
# compute timestamp and climb rate
for i, data in enumerate(rawdata):

    newData = data
    if i:
        deltaTime = float(data[0]) - float(rawdata[i - 1][0])
        climbfpm = float(data[3]) - float(rawdata[i - 1][3])
        newData.append(deltaTime)
        newData.append(climbfpm / deltaTime * 60)
    else:
        newData.append(0)
        newData.append(0)

    computedData.append(newData)

makeGraph(computedData)
