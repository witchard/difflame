difflame
========

A lame tool for visualising diffs! This tool uses flamegraphs (http://www.brendangregg.com/flamegraphs.html) to visualise the differences within git repositories.

* Installation: `pip install difflame`.
* View diffs: `cd <git-repo>; difflame.py`. Then visit http://localhost:1234.
* More options: `difflame.py --help`.

For large repositories it is recommended you create your diffs offline with `difflame.py save`, and then visualise with `difflame.py servefiles`.
