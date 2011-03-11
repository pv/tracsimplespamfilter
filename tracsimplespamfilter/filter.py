# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

from StringIO import StringIO

import sys
import os
import re
import cgi
import urllib
import datetime

from trac.util.datefmt import utc
from trac.core import *
from trac.config import Option, IntOption, ListOption, BoolOption
from trac.web.api import IRequestFilter, IRequestHandler, Href
from trac.wiki.api import IWikiSyntaxProvider
from trac.util.translation import _
from trac.attachment import IAttachmentManipulator
from trac.mimeview import is_binary
from trac.ticket import ITicketManipulator, TicketSystem
from trac.util.text import to_unicode
from trac.wiki import WikiPage, IWikiPageManipulator

class RejectContent(TracError):
    """Exception raised when content is rejected by a filter."""

class TracSimpleSpamFilterPlugin(Component):
    implements(ITicketManipulator)#, IWikiPageManipulator, IAttachmentManipulator)

    regex = Option('tracsimplespamfilter', 'regex', '',
                   doc="Spam-forbidding regular expressions")
    allow = Option('tracsimplespamfilter', 'allow', '',
                   doc="Filter skipping permission group")

    sample_size = 65536

    def __init__(self):
        self.regexps = [re.compile(x, re.S|re.U) for x in self.regex.split(';')]

    def _check_allow(self, req, extra):
        if self.allow:
            for group in self.allow.split(";"):
                if req.perm.has_permission(group):
                    return True
        return req.perm.has_permission(extra)

    def check(self, changes):
        changes = u"".join(changes)
        for expr in self.regexps:
            m = expr.search(changes)
            if m:
                raise RejectContent("Content rejected")

    # ITicketManipulator methods

    def prepare_ticket(self, req, ticket, fields, actions):
        pass

    def validate_ticket(self, req, ticket):
        if self._check_allow(req, 'TICKET_ADMIN'):
            # An administrator is allowed to spam
            return []

        changes = []

        # Add any modified text fields of the ticket
        fields = [f['name'] for f in
                  TicketSystem(self.env).get_ticket_fields()
                  if f['type'] in ('textarea', 'text')]
        for field in fields:
            if ticket.exists and field == 'description':
                continue
            if field in ticket._old:
                changes.append(ticket[field])

        if 'comment' in req.args:
            changes.append(req.args.get('comment'))

        self.check(changes)

        return []

#    # IWikiPageManipulator methods
#
#    def prepare_wiki_page(self, req, page, fields):
#        pass
#
#    def validate_wiki_page(self, req, page):
#        if self._check_allow(req, 'WIKI_ADMIN'):
#            # An administrator is allowed to spam
#            return []
#
#        text = page.text
#        comment = req.args.get('comment')
#
#        # Test the actual page changes as well as the comment
#        changes = [text]
#        if comment:
#            changes += [comment]
#
#        self.check(changes)
#
#        return []
#
#    # IAttachmentManipulator methods
#
#    def prepare_attachment(self, req, attachment, fields):
#        pass
#
#    def validate_attachment(self, req, attachment):
#        if self._check_allow(req, 'WIKI_ADMIN'):
#            # An administrator is allowed to spam
#            return []
#
#        author = req.args.get('author', req.authname)
#        description = req.args.get('description')
#
#        filename = None
#        upload = req.args.get('attachment')
#        content = ''
#        if upload is not None:
#            try:
#                data = upload.file.read(self.sample_size)
#                if not is_binary(data):
#                    content = to_unicode(data)
#            finally:
#                upload.file.seek(0)
#            filename = upload.filename
#
#        changes = [x for x in (description, filename, content) if x]
#
#        self.check(changes)
#
#        return []
