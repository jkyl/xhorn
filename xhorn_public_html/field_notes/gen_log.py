from subprocess import call
HTML = '''
<HTML>
<HEAD>
<TITLE>X-band el tipping radiometer field notes</TITLE>
</HEAD>
<BODY TEXT="#000000" BGCOLOR="#F0F0F0">
<CENTER>
<H1>X-band el tipping radiometer field notes</H1>
Update to latest version by running <tt> $python ~xhorn/public_html/field_notes/gen_log.py</tt>
<p>
</CENTER>
<head>
<style>
table, th, td {{
    border: 1px solid black;
    border-collapse: collapse;
}}
th, td {{
    padding: 5px;
}}
</style>
</head>
<body>
<table style="width:100%">
  {}
</table>
</body>
<p><HR width=100%>
</BODY>
</HTML>
'''

def read_log(f='/home/xhorn/public_html/field_notes/log.csv'):
    '''
    '''
    rv = ''
    with open(f) as log:
        for line in log:
            fields = line.split(',')
            row = ('<tr>' + '<td>{}</td>'*len(fields) + '</tr>').format(*fields)
            rv += row
    return rv

def pull_log(url='https://raw.githubusercontent.com/jkyl/xhorn/master/log.csv'):
    '''
    '''
    call(['wget', url, '-O', '/home/xhorn/public_html/field_notes/log.csv'])

if __name__ == '__main__':
    pull_log()
    entries = read_log()
    HTML = HTML.format(entries)
    with open('/home/xhorn/public_html/field_notes/index.html', 'w+') as f:
        f.write(HTML)
    
    
