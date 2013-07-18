#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: Lyx2Informs.py 601 2011-05-23 08:22:05Z lleeoo $
# Freely distributable under the MIT license

# Reformat a latex file exported from lyx, using the article(AMS) template,
# so that it can be used with the OR informs2 class.
# Write the output to stdout.

import re

class Lyx2Informs:
  """Reformat a latex file exported from LyX using the paper(AMS) document class
  for use with the INFORMS informs2 class."""
  def __init__(self,inputFileName):
    """load the original file and the reference to the informs2 class."""
    self.doc = open(inputFileName).read()
    
  def main(self):
    self.changeDocumentClass()
    self.addPreambleSugar()
    self.removeDoublespace()
    self.removeComments()
    self.changeTitle()
    self.changeAuthors()
    self.changeAbstract()
    self.changeKeywords()
    self.changeFootnoteToEndnote()
    self.changeAck()
    self.changeAppendix()
    self.changeFigures()
    self.fixBugs()
    print self.doc
    
  def replaceSnippet(self,startEnd,newString):
    """Replace an inner portion of self.doc with the new string"""
    self.doc = "%s%s%s" % (self.doc[:startEnd[0]], newString, self.doc[startEnd[1]:])
    
  def changeDocumentClass(self):
    """Change the document class to informs2 and preserve options"""
    s = re.search(r"^\\documentclass([^{]*)\{amsart\}",self.doc,flags=re.M)
    if s:
      options = ""
      if len(s.groups()[0]): options = ","+s.groups()[0][1:-1]
      self.replaceSnippet(s.span(),"\\documentclass[opre,nonblindrev,copyedit%s]{informs2}" % options)
    else: raise Exception, "No \documentclass found!"
  
  def addPreambleSugar(self):
    """Copies some stuff from the OR template to the preamble of the file."""
    preambleSugar = \
r"""\usepackage{endnotes}
\let\footnote=\endnote
\let\enotesize=\normalsize
\def\notesname{Endnotes}%
\def\makeenmark{$^{\theenmark}$}
\def\enoteformat{\rightskip0pt\leftskip0pt\parindent=1.75em
  \leavevmode\llap{\theenmark.\enskip}}

% Private macros here (check that there is no clash with the style)

% Natbib setup for author-year style
\usepackage{natbib}
 \bibpunct[, ]{(}{)}{,}{a}{}{,}%
 \def\bibfont{\small}%
 \def\bibsep{\smallskipamount}%
 \def\bibhang{24pt}%
 \def\newblock{\ }%
 \def\BIBand{and}%

%% Setup of theorem styles. Outcomment only one.
%% Preferred default is the first option.
\TheoremsNumberedThrough     % Preferred (Theorem 1, Lemma 1, Theorem 2)
%\TheoremsNumberedByChapter  % (Theorem 1.1, Lema 1.1, Theorem 1.2)
\ECRepeatTheorems

%% Setup of the equation numbering system. Outcomment only one.
%% Preferred default is the first option.
\EquationsNumberedThrough    % Default: (1), (2), ...
%\EquationsNumberedBySection % (1.1), (1.2), ...

% In the reviewing and copyediting stage enter the manuscript number.
%\MANUSCRIPTNO{} % When the article is logged in and DOI assigned to it,
                 %   this manuscript number is no longer necessary

"""
    s = re.search(r"^\\begin{document}",self.doc,re.M)
    self.replaceSnippet((s.start(),s.start()),preambleSugar)
    
  def removeDoublespace(self):
    """remove \doublespacing if present."""
    s = re.search(r"^\\doublespacing",self.doc,flags=re.M)
    if s: self.replaceSnippet(s.span(),"")
    package = re.search(r"^\\usepackage\{setspace\}",self.doc,re.M)
    if package: self.replaceSnippet((package.start(),package.end()),"")
          
  def removeComments(self):
    """remove LyX \begin{comment}...\end{comment} environments if present."""
    for fig in reversed(self.findAllEnvironments('comment')):
      self.replaceSnippet((fig['start'],fig['end']),'')
      
  def changeTitle(self):
    """replace \title with \TITLE and look for \RUNTITLE lyx comment."""
    s = self.findCommand("title")
    if s:
      rs = re.search(r"^\\textbackslash{}RUNTITLE\\{(.*)\\",self.doc,re.M)
      if rs: runtitle = "\\RUNTITLE{%s}\n" % rs.groups()[0]
      else: runtitle = ""
      self.replaceSnippet((s['start'],s['end']),"")
      ms = re.search(r"^\\maketitle",self.doc,re.M)
      self.replaceSnippet((ms.start(),ms.start()),"\\TITLE{%s}\n%s" % (s['content'],runtitle ))
    else: raise Exception, "No \\title found!"
      
  def changeAuthors(self):
    """Use Authors one-by-one (not using ERT \AND), 
    and add affiliations as Address in lyx, followed by the Email of the author,
    each in its own paragraph.""" 
    # This transformation will require a pretty complicated new string to be built.
    # get the first and last location of the original string from the match information.
    authorInfo = "\\ARTICLEAUTHORS{%%\n"
    s = self.findAllCommands('author')
    start = s[0]['start']
    authors = [si['content'] for si in s]
    if len(authors):
      nAuthors = len(authors)
      addresses = [si['content'] for si in self.findAllCommands('address')]
      s = self.findAllCommands('email')
      end = s[-1]['end']
      emails = [si['content'].strip() for si in s]
      if len(addresses) == len(emails) == nAuthors:        
        email = ""
        for ai in range(nAuthors-1):
          if email: email += ",%s" % emails[ai]
          else: email = emails[ai]
          authorInfo += "\\AUTHOR{%s}\n" % authors[ai]
          # check if this author has a separate affiliation.
          if addresses[ai] != addresses[ai+1]:
            authorInfo += "\\AFF{%s, \EMAIL{%s}}\n" % (addresses[ai],email)
            email = ""
        # always print info for last author
        authorInfo += "\\AUTHOR{%s}\n" % authors[-1]
        if email: email += ",%s" % emails[-1]
        else: email = emails[-1]
        authorInfo +=  "\\AFF{%s, \EMAIL{%s}}\n}\n%% end of ARTICLEAUTHORS\n" % (addresses[-1],email)
        lastNames = [names[-1] for names in (ai.split() for ai in authors)]
        if nAuthors == 1: authorInfo += "\\RUNAUTHOR{%s}\n" % lastNames
        elif nAuthors == 2: authorInfo += "\\RUNAUTHOR{%s and %s}\n" % tuple(lastNames)
        elif nAuthors == 3: authorInfo += "\\RUNAUTHOR{%s, %s and %s}\n" % tuple(lastNames)
        else: authorInfo += "\\RUNAUTHOR{%s et al.}\n" % lastNames[0]
        self.replaceSnippet((start,end),"")
        ms = re.search(r"^\\maketitle",self.doc,re.M)
        self.replaceSnippet((ms.start(),ms.start()),authorInfo)
      else: raise Exception, "Missing author information! We assume everyone has an address and email."
    else: raise Exception, "No authors found!"
  
  def changeAbstract(self):
    """replace \\begin{abstract} ... \\end{abstract} with \\ABSTRACT{...}"""
    s = self.findEnvironment('abstract')
    if s:
      self.replaceSnippet((s['start'],s['end']),"")
      ms = re.search(r"^\\maketitle",self.doc,re.M)
      self.replaceSnippet((ms.start(),ms.start()),"\\ABSTRACT{%%\n%s}%%\n" % s['content'])
    else: raise Exception, "No abstract found!"
      
  def changeKeywords(self):
    """replace \keywords with \KEYWORDS."""
    s = self.findCommand('keywords')
    if s:
      self.replaceSnippet((s['start'],s['end']),"")
      ms = re.search(r"^\\maketitle",self.doc,re.M)
      self.replaceSnippet((ms.start(),ms.start()),"\\KEYWORDS{%s}\n" % s['content'])
      
  def changeFootnoteToEndnote(self):
    """add \theendnote if \footnotes found."""
    s = self.findCommand('footnote')
    if s:
      bs = re.search(r"^\\bibliographystyle",self.doc,re.M)
      if bs:
        self.replaceSnippet((bs.start(),bs.start()),"\\theendnotes\n")
      else: raise Exception, "No \\bibliographystyle!"

  def changeAck(self):
    """replace \dedicatory with \ACKNOWLEDGMENT."""
    s = self.findCommand('dedicatory')
    if s:
      self.replaceSnippet((s['start'],s['end']),"")
      bs = re.search(r"^\\bibliographystyle",self.doc,re.M)
      if bs:
        self.replaceSnippet((bs.start(),bs.start()),"\\ACKNOWLEDGMENT{%s}\n" % s['content'])
      else: raise Exception, "No \\bibliographystyle!"
      
  def changeAppendix(self):
    """replace \appendix declaration with \begin{APPENDICES}...\end{APPENDICES}"""
    s = self.findCommand('appendix')
    if s:
      appendixCmdStart, appendixCmdEnd = s['start'],s['end']
      bs = self.findCommand('bibliographystyle')
      if bs:
        newSection = "\\begin{APPENDICES}\n%s\\end{APPENDICES}\n" % self.doc[appendixCmdEnd:bs['start']]
        self.replaceSnippet((appendixCmdStart,bs['start']),newSection)
      else: raise Exception, "No \\bibliographystyle!"
  
  def changeFigures(self):
    """Add the informs2.cls definitions for \FIGURE (if needed)"""
    for fig in reversed(self.findAllEnvironments('figure')):
      # remove all occurences of \par in figures.
      caption = self.findCommand('caption',fig['content'])
      mainContent = fig['content'][:caption['start']] + fig['content'][caption['end']:]
      # filter out empty lines
      mainContent = '\n'.join([l for l in mainContent.splitlines() if l != ''])
      for cmd in reversed(self.findAllCommands('par',mainContent)):
        # print (fig['start'],cmd['start'],fig['start'],cmd['end'])
        # print self.doc[fig['start']+cmd['start']:fig['start']+cmd['end']]
        mainContent = mainContent[:cmd['start']]+mainContent[cmd['end']:]
      newFig = "\\begin{figure}\n\\FIGURE{%s}\n{%s}\n{}\n\\end{figure}" % (
        mainContent,caption['content']
      )
      self.replaceSnippet((fig['start'],fig['end']),newFig)
    
      
  def findEnvironment(self,opening,doc=None):
    """find the matching latex group in 'doc' looking for \\begin and \\end environment. 
    Assumes the group starts a line."""
    if not doc: doc = self.doc
    s = re.search(r"^\\begin{%s}" % opening,doc,flags=re.M|re.DOTALL)
    if s:
      e = re.search(r"^\\end{%s}" % opening,doc[s.end():],flags=re.M|re.DOTALL)
      match = {'start':s.start(),'end':s.end()+e.end(),
        'group':doc[s.start():s.end()+e.end()], 'content':doc[s.end():s.end()+e.start()]
      }
    else: match=None
    return match
    
  def findCommand(self,command,doc=None):
    """find the matching latex command in 'doc' counting { and }"""
    if doc == None: doc = self.doc
    s = re.search(r"\\%s(?P<optional>\[[^]]+\])?(?P<arguments>{)?" % command,doc,flags=re.M|re.DOTALL)
    if s:
      # check if there are arguments and capture them until the number
      # of '{' and '}' match.
      stringStart = s.end()
      if s.groupdict()['arguments']: count = 1
      else: count = 0
      while count:
        e = re.search(r"([{}])",doc[stringStart:],flags=re.M|re.DOTALL)
        if e.group() == '{': count += 1
        else: count -=1
        stringStart += e.end()
      match = {'start':s.start(),'end':stringStart,
        'group':doc[s.start():stringStart], 'content':doc[s.end():stringStart-1]
      }
    else: match=None
    return match

  def findAllGeneric(self,opening,fun,doc):
    """Avoid duplicate code. 
    When finding multiple environments call this function with the environment-finding
    function as a parameter"""
    if doc == None: doc = self.doc
    start, groups = 0, []
    group = fun(opening,doc)
    while group:
      group['start'], group['end'] = group['start'] + start, group['end'] + start
      groups.append(group)
      start = group['end']
      group = fun(opening,doc[start:])
    return groups

  def findAllEnvironments(self,opening,doc=None):
    """find all environements with this opening."""
    return self.findAllGeneric(opening,self.findEnvironment,doc)

  def findAllCommands(self,opening,doc=None):
    """find all commands with this opening."""
    return self.findAllGeneric(opening,self.findCommand,doc)
              
  
  def fixBugs(self):
    """Miscelaneous fixes needed to get the source to compile go here. They include:
    * commenting out amsthm, which conflicts with the theorems defined in informs2
    * replace ams 'thm' with informs2 'theorem'
    * that's it for now."""
    amsthm = re.search(r"^\\usepackage\{amsthm\}",self.doc,re.M)
    if amsthm: self.replaceSnippet((amsthm.start(),amsthm.end()),"")
    amsthm = re.search(r"^\\newtheorem\{thm\}\{Theorem\}",self.doc,re.M)
    if amsthm: self.replaceSnippet((amsthm.start(),amsthm.end()),"")
    allthms = [t for t in re.finditer(r"\{thm\}",self.doc)]
    allthms.reverse() # since the string will change in size every time we make a substitution
    for t in allthms: self.replaceSnippet((t.start(),t.end()),r"{theorem}")
    subfig = re.search(r"^\\usepackage\{subfig\}",self.doc,re.M)

  
if __name__ == '__main__':
  import sys
  if len(sys.argv) != 2: sys.stderr.write(\
  """Convert a tex file exported from a lyx article(AMS) into an INFORMS submission.
  Usage: %s <inputfile>
""" % sys.argv[0])
  else: Lyx2Informs(sys.argv[1]).main()
