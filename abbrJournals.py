#!/usr/bin/env python
# $Id: abbrJournals.py 246 2008-02-29 03:48:20Z leolopes $
# update your bib files with the abbreviations at:
# http://www.informs.org/site/IJOC/article.php?id=64
#
# Created by: Leo Lopes, 2/2008
# THIS FILE IS IN THE PUBLIC DOMAIN

abbreviations = {
"Academy":"Acad.",
"Adaptive":"Adapt.",
"Administrative":"Admin.",
"Advances":"Adv.",
"American":"Amer.",
"Analysis":"Anal.",
"Annals":"Ann.",
"Applications":"Appl.", "Applied":"Appl.",
"Archives":"Arch.",
"Biology":"Biol.", "Biological":"Biol.",
"Bulletin":"Bull.",
"Business":"Bus.",
"Collection":"Collect.",
"Combinatorial":"Combin.",
"Communication":"Comm.", "Communications":"Comm.",
"Computer":"Comput.", "Computation":"Comput.", "Computing":"Comput.",
"Conference":"Conf.",
"Continuous":"Contin.",
"Cuaderno":"Cuad.", "Cuadernos":"Cuad.",
"Dynamics":"Dynam.",
"Economic":"Econom.", "Economical":" Econom.", "Economy":" Econom.",
"Education":"Ed.",
"Electrical":"Electr.",
"Elements":"Elem.",
"Engineering":"Engrg.",
"Environmental":"Environ.",
"European":"Eur.",
"Experimental":"Experiment.",
"Faculty":"Fac.",
"Functional":"Funct.",
"Functional":"Hist.", "Historical":"Hist.", "History":"Hist.",
"Industrial":"Indust.", "Industry":"Indust.",
"Information":"Inform.",
"Institute":"Inst.",
"International":"Internat.",
"Journal":"J.",
"Learning":"Learn.",
"Letters":"Lett.",
"Logistics":"Logist.",
"Mathematics":" Math.", "Mathematical":" Math.",
"Mechanical":"Mech.", "Mechanics":"Mech.",
"Modeling":"Model.", "Modelling":"Model.",
"Natural":"Nat.",
"Numerical":"Numer.",
"Operational":"Oper.", "Operations":"Oper.",
"Optimization":"Optim.",
"Organization":"Organ.",
"Organizational":"Organ.",
"Philosophical":"Philos.",
"Philosophy":"Philos.",
"Physics":"Phys.",
"Probability":"Probab.",
"Proceedings":"Proc.",
"Psychological":"Psych.", "Psychology":"Psych.", "Psychological":"Psych.",
"Publications":"Publ.",
"Quantitative":"Quant.",
"Quarterly":"Quart.",
"Recherche":"Rech.",
"Reports":"Rep.",
"Research":"Res.",
"Review":"Rev.",
"Royal":"Roy.",
"Science":"Sci.", "Scientific":"Sci.",
"Section":"Sect.",
"Series":"Ser.",
"Social":"Soc.", "Society":"Soc.",
"Statistics":"Statist.", "Statistical":"Statist.",
"Study":"Studies Stud.", "Studies":"Stud.",
"Symposium":"Sympos.",
"Technological":"  Tech.", "Technology":" Tech.", "Technical":" Tech.",
"Telecommunications":"Telecomm.",
"Theoretical":"Theoret.",
"Transactions":"Trans.",
"University":"Univ.",
}

from sys import stdin, stdout # stdout needed. print will add space.
import re

res = {} # convert words into regular expressions only once
for word in abbreviations: res[re.compile(word)] = abbreviations[word]
journal = re.compile("journal\\s*?=.*?,",re.I)

bib = stdin.read()
if not len(bib): exit(1)

j = journal.search(bib)
while j:
	stdout.write(bib[:j.start() + 7]) # 7 is the length of the word 'journal'
	s = bib[j.start() + 7:j.end()]
	for r in res: s = r.sub(res[r],s)
	stdout.write(s)
	bib = bib[j.end():]
	j = journal.search(bib)
stdout.write(bib)
