#!/usr/bin/env python3

import git
import sys
import collections
import json
import grole
import logging
import argparse
import pathlib

logging.basicConfig(level=logging.INFO)

# ---------- Helper functions ----------
def intOr1(val):
    try:
        return int(val)
    except ValueError:
        return 1

def tree():
    return {'children': collections.defaultdict(tree)}

def getNode(tree, names):
    for name in names:
        tree = tree['children'][name]
    return tree

def countDiffs(tree, basename='root'):
    # Local diffs
    out = {}
    out['value'] = 0
    out['added'] = 0
    out['removed'] = 0
    if 'added' in tree:
        out['value'] += tree['added']
        out['added'] += tree['added']
    if 'removed' in tree:
        out['value'] += tree['removed']
        out['removed'] += tree['removed']

    # Set name
    out['name'] = basename

    # Recurse into child nodes summing diffs
    if len(tree['children']):
        out['children'] = []
        for name, subtree in tree['children'].items():
            child = countDiffs(subtree, name)
            out['value'] += child['value']
            out['added'] += child['added']
            out['removed'] += child['removed']
            out['children'].append(child)
    
    return out

def getChanges(path, from_rev, to_rev):
    changes = tree()
    repo = git.Repo.init(path)
    diffs = repo.git.diff(['--numstat', from_rev, to_rev])
    for line in diffs.split('\n'):
        info = line.split(maxsplit=3)
        node = getNode(changes, info[2].split('/'))
        node['added'] = intOr1(info[0])   # intOr1 copes with binary files
        node['removed'] = intOr1(info[1])
    return countDiffs(changes)

# ---------- Web Server ----------
def doServe(address, port, mode, serve_arg):
    app = grole.Grole({'mode': mode, 'arg': serve_arg})

    @app.route('/')
    def index(env, req):
        html = '''
<head>
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/spiermar/d3-flame-graph@1.0.10/dist/d3.flameGraph.min.css">
</head>
<body>
  <div style='text-align: center'>'''
        if mode == 'diffs':
            html += '''
    <form method="GET">
      From: <input type="text" name="from">
      To: <input type="text" name="to">
      <input type="submit" value="Generage">
    </form>'''
        else:
            html += '''
    <form method="GET">
      <select name="file">'''
            for f in serve_arg:
              html += '<option value="{}">{}</option>'.format(f.name, f.name)
            html += '''
      </select>
      <input type="submit" value="Generage">
    </form>'''

        html += '''
    <div id="chart"></div>
    <div id="details"></div>
  </div>
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.10.0/d3.min.js"></script>
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3-tip/0.7.1/d3-tip.min.js"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/gh/spiermar/d3-flame-graph@1.0.10/dist/d3.flameGraph.min.js"></script>
  <script type="text/javascript">

  function label(d) {
    return d.data.name + " (" +
           d.data.added + " added, " +
           d.data.removed + " removed, " +
           d3.format(".3f")(100 * (d.x1 - d.x0), 3) + "%)";
  }

  var flamegraph = d3.flameGraph()
    .width(960)
    .label(label)
    .tooltip(false)
    .details(document.getElementById("details"));

  d3.json("data" + window.location.search, function(error, data) {
    if (error) return console.warn(error);
    d3.select("#chart")
      .datum(data)
      .call(flamegraph);
  });
  </script>
</body>
'''
        return grole.ResponseString(html, 'text/html')

    @app.route('/data')
    def data(env, req):
        if env['mode'] == 'diffs':
            return getChanges(env['arg'], req.query.get('from', 'HEAD~1'),
                req.query.get('to', 'HEAD'))
        else:
            return grole.ResponseFile(req.query.get('file', env['arg'][0].name))

    app.run(address, port)

# ---------- Main ----------
def parse_args(args):
    if len(args) == 0:
      args = ['serve'] # Default is to serve

    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(help='commands', dest='command')

    serve = sub.add_parser('serve', help='serve diff information (default)')
    serve.add_argument('-d', '--directory', default='.',
        help='directory to look for repository, default: .')
    serve.add_argument('-a', '--address', default='localhost',
        help='address to listen on, default: localhost')
    serve.add_argument('-p', '--port', default=1234, type=int,
        help='port to listen on, default: 1234')

    serve_files = sub.add_parser('servefiles',
        help='serve diff information from files')
    serve_files.add_argument('file', nargs='+', type=argparse.FileType('r'), 
      help='files to serve')
    serve_files.add_argument('-a', '--address', default='localhost',
        help='address to listen on, default: localhost')
    serve_files.add_argument('-p', '--port', default=1234, type=int,
        help='port to listen on, default: 1234')

    save = sub.add_parser('save', help='save diff information to a file')
    save.add_argument('-d', '--directory', default='.',
        help='directory to look for repository, default: .')
    save.add_argument('file', nargs='?', type=argparse.FileType('w'),
        default=sys.stdout, help='file to save to, default: stdout')
    save.add_argument('-f', '--from', default='HEAD~1', dest='from_ref',
        help='commit to start from, defaut: HEAD~1')
    save.add_argument('-t', '--to', default='HEAD',
        help='commit to end on, default: HEAD')

    ret = parser.parse_args(args)
    if (ret.command == 'save' or ret.command == 'serve') and \
       (not pathlib.Path(ret.directory).is_dir()):
      parser.error('argument -d/--directory: expected a valid directory')

    return ret

def main(args=sys.argv[1:]):
  args = parse_args(args)
  if args.command == 'save':
    changes = getChanges(args.directory, args.from_ref, args.to)
    json.dump(changes, args.file)
  elif args.command == 'servefiles':
    doServe(args.address, args.port, 'files', args.file)
  elif args.command == 'serve':
    doServe(args.address, args.port, 'diffs', args.directory)


if __name__ == '__main__':
    main()
