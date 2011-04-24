====================
tracsimplespamfilter
====================

Utterly simplistic spam filter that rejects content based on regexps.

Watches over ticket edits.

Configuration
============

::

        [components]
        tracsimplespamfilter.* = enabled

        [tracsimplespamfilter]
        regex = regex1;regex2;regex3;...
        allow = some_trac_group

