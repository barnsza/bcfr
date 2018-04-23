import glob
import re
import datetime
import bokeh.plotting
import bokeh.palettes

files = glob.glob('bcfr.log*')

charts = dict()

for fn in files:
    with open(fn) as f:
        for l in f:
            parts = [ x.strip() for x in l.split('/') ]

            # Request is 2 parts ; Reply is 3 parts
            if len(parts) != 2 and len(parts) != 3:
                raise ValueError()

            date, type, client = re.match('(.*) \[DNSHandler:BCFR\] (.*): \[(.*):.*\] \(udp\)', parts[0]).groups()
            host, = re.match('\'(.*)\' .*', parts[1]).groups()

            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            # date = dadate.replace(minute=0, second=0)
            # date = date.replace(second=0)
            date = date - datetime.timedelta(minutes=date.minute % 10, seconds=date.second)

            reply = ''
            if type == 'Reply':
                reply = '-' + parts[2].split(':')[0]

            chart = f'{type}{reply}'
            if not chart in charts: charts[chart] = dict()
            if not date in charts[chart]: charts[chart][date] = 0
            charts[chart][date] += 1

bp = bokeh.plotting.figure(title='BCFR Statistics', width=600, height=300, x_axis_type="datetime")

start_time = min([min(charts[x].keys()) for x in charts.keys()])
end_time = max([max(charts[x].keys()) for x in charts.keys()])

for type in charts.keys():
    current_time = start_time - datetime.timedelta(minutes=10)
    while current_time < end_time:
        current_time = current_time + datetime.timedelta(minutes=10)
        if not current_time in charts[type]: charts[type][current_time] = 0

# colours = ['red', 'green', 'blue', 'orange', 'purple']
# colours = bokeh.palettes.viridis(len(charts.keys()))
colours = bokeh.palettes.d3['Category10'][len(charts.keys())]
for idx, type in enumerate(charts.keys()):
    times = sorted(charts[type].keys())
    values = [charts[type][x] for x in times]
    bp.line(times, values, color=colours[idx], legend=type)
    # break

bp.legend.location = "top_left"
# bp.legend.orientation = "horizontal"
bokeh.plotting.show(bp)
