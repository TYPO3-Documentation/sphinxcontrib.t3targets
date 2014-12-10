# -*- coding: utf-8 -*-
"""
    sphinxcontrib.t3targets
    ~~~~~~~~~~~~~~~~~~~~~

    Allow a list of all labels of the std domain to be inserted into your
    documentation.

    :copyright: Copyright 2012-2099 by the TYPO3 team, see AUTHORS.
    :license: BSD, see LICENSE for details.
    :author: Martin Bless <martin@mbless.de>

"""

__license__ = """

If not otherwise noted, the extensions in this package are licensed
under the following license.

Copyright (c) 2011 by the contributors (see AUTHORS.rst file).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

# 2012-11-04, mb: It seems to work! So let's try it :-)

# Tipp: see
#       http://nullege.com/codes/search/docutils.nodes.reference

from docutils import nodes
from sphinx.util.compat import Directive
from operator import itemgetter
import os

def getRelPath(srcdir, destpath):
    # srcdir = 'a/b/c'
    # destpath = 'a/b/d/x.html'
    # credit:
    # http://code.activestate.com/recipes/302594-another-relative-filepath-script/
    srclist = os.path.abspath(srcdir).split(os.sep)
    destlist = os.path.abspath(destpath).split(os.sep)
    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    for i in range(min(len(srclist), len(destlist))):
        if srclist[i] <> destlist[i]:
            break
    else:
        # If we broke out of the loop, i is pointing to the first differing
        # path elements. If we didn't break out of the loop, i is pointing
        # to identical path elements. Increment i so that in all cases it
        # points to the first differing path elements.
        i += 1
    rellist = [os.pardir] * (len(srclist)-i) + destlist[i:]
    return os.path.join(*rellist)


class reftargetslist_node(nodes.General, nodes.TextElement):
    pass

class RefTargetsList(Directive):
    """Insert node for the ref-targets-list.

    """
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        # save the destination docname so that we can
        # build relative paths to it later
        node = reftargetslist_node(text=env.docname)
        return [node]

## <bullet_list bullet="-" classes="simple">
##    <list_item>
##       <paragraph classes="first">
##           aaaaa
##    <list_item>
##       <paragraph classes="first">
##           bbbbb
##    <list_item>
##       <paragraph classes="first">
##           ccccc

##
##    <definition_list classes="docutils">
##       <definition_list_item>
##          <term>
##             Property
##          <definition>
##             <paragraph classes="first last">
##                 Name of the property
##

## <reference classes="reference\ internal" internal="True"
##            refuri="../NextSteps/Index.html#next-steps">

def keyfunc(item):
    # make key to sort document paths
    itemlist = item.replace('\\', '/').lower().split('/')
    listlen = len(itemlist)
    for i in range(len(itemlist)):
        # files first, then subfolders
        itemlist[i] = '%s%s' % (0 if i+1==listlen else 1, itemlist[i])
    return '/'.join(itemlist)

def process_reftargetslist_nodes(app, doctree, fromdocname):
    env = app.builder.env
    etc = env.ext_targets_cache
    cntLabels = 0
    cntAnonLabels = 0
    for node in doctree.traverse(reftargetslist_node):
        # srcdir = folder path to document with
        # ref-targets-list directive
        srcdir = os.path.split(node.astext())[0]
        definition_list = nodes.definition_list(
            classes=['ref-targets-list'])
        labels = env.domains['std'].data['labels']
        anonlabels = env.domains['std'].data['anonlabels']
        for doc in sorted(etc.keys(), key=keyfunc):
            relpath = getRelPath(srcdir, doc).replace('\\','/')
            relpath = os.path.splitext(relpath)[0] + '.html'
            rstrelpath = os.path.join('_sources', doc)
            rstrelpath = getRelPath(srcdir, rstrelpath).replace('\\','/')
            rstrelpath = os.path.splitext(rstrelpath)[0] + '.txt'
            bullet_list = nodes.bullet_list(rawsource='', bullet='-')
            for lineno, refid in sorted(etc[doc], key=itemgetter(0)):
                if labels.has_key(refid):
                    flag = 'label'
                    cntLabels += 1
                elif anonlabels.has_key(refid):
                    flag = 'anonlabel'
                    cntAnonLabels += 1
                else:
                    flag = None
                if flag:
                    linktext1 = '%04d' % lineno
                    refuri1 = '%s?refid=%s&line=%s' % (rstrelpath,
                                                       refid, lineno)
                    reftitle1 = None
                    reference1 = nodes.reference(text=linktext1,
                                                 internal=True,
                                                 refuri=refuri1,
                                                 classes=['e2'])

                    if flag == 'label':
                        linktext2 = ':ref:`%s`' % refid
                        reftitle2 = labels[refid][2]
                    else:
                        linktext2 = ':ref:`... <%s>`' % refid
                        reftitle2 = None

                    refuri2 = '%s#%s' % (relpath, refid)
                    if reftitle2:
                        reference2 = nodes.reference(text=linktext2,
                                                     internal=True,
                                                     refuri=refuri2,
                                                     reftitle=reftitle2,
                                                     classes=['e4'])
                    else:
                        reference2 = nodes.reference(text=linktext2,
                                                     internal=True,
                                                     refuri=refuri2,
                                                     classes=['e4'])

                    paragraph = nodes.paragraph()
                    paragraph.append(nodes.inline(text='[',
                                                  classes=['e1']))
                    paragraph.append(reference1)
                    paragraph.append(nodes.inline(text='] ',
                                                  classes=['e3']))
                    paragraph.append(reference2)
                    list_item = nodes.list_item()
                    list_item.append(paragraph)
                    bullet_list.append(list_item)

            if len(bullet_list):
                term = nodes.term(text=doc)
                definition = nodes.definition()
                definition.append(bullet_list)
                definition_list_item = nodes.definition_list_item()
                definition_list_item.append(term)
                definition_list_item.append(definition)
                definition_list.append(definition_list_item)

        summary = ('Summary: %s targets (%s with link text, %s without).' %
                   (cntLabels + cntAnonLabels, cntLabels, cntAnonLabels))
        summaryP = nodes.paragraph(text=summary,
                                   classes=['ref-targets-list-summary'])
        node.replace_self([definition_list, summaryP])

def visit_reftargetslist_node(self, node):
    self.visit_paragraph(node)

def depart_reftargetslist_node(self, node):
    self.depart_paragraph(node)


##Sphinx core events (hooks)
##
##http://sphinx-doc.org/latest/ext/appapi.html#sphinx-core-events
##
##builder-inited(app)
##env-get-outdated(app, env, added, changed, removed)
##env-purge-doc(app, env, docname)
##source-read(app, docname, source)
##doctree-read(app, doctree)
##missing-reference(app, env, node, contnode)
##doctree-resolved(app, doctree, docname)
##env-updated(app, env)
##html-collect-pages(app)
##html-page-context(app, pagename, templatename, context, doctree)
##build-finished(app, exception)

def doctreeRead(app, doctree):
    env = app.builder.env
    docname = env.docname
    if not hasattr(env, 'ext_targets_cache'):
        env.ext_targets_cache = {}
    etc = env.ext_targets_cache
    if not etc.has_key(docname):
        etc[docname] = []
    for node in doctree.traverse(nodes.target):
        if node.attributes.has_key('refid'):
            etc[docname].append((node.line, node.attributes['refid']))

def setup(app):
    app.add_node(
        reftargetslist_node,
        html=(visit_reftargetslist_node, depart_reftargetslist_node),
        latex=(visit_reftargetslist_node, depart_reftargetslist_node),
        text=(visit_reftargetslist_node, depart_reftargetslist_node),
        man=(visit_reftargetslist_node, depart_reftargetslist_node),
        texinfo=(visit_reftargetslist_node, depart_reftargetslist_node),
        )
    app.add_directive('ref-targets-list', RefTargetsList)
    app.connect('doctree-read', doctreeRead)
    app.connect('doctree-resolved', process_reftargetslist_nodes)
