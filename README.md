difflame
========

A lame tool for visualising diffs! This tool uses flamegraphs (http://www.brendangregg.com/flamegraphs.html) to visualise the differences within git repositories.

* Installation: Put difflame in your path somewhere.
* View diffs: `cd <git-repo>; difflame`. Then visit http://localhost:1234.
* More options: `difflame --help`.

For large repositories it is recommended you create your diffs offline with `difflame save`, and then visualise with `difflame servefiles`.
