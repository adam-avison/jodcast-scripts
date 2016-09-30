#------------------------------------------------------------------------#
#  A file full of 'helpful' functions and data to help jodcastxml.py     #
#  Created by Adam Avison 22/01/2015                                     #
#  Comments starting <AA> were written by me. If you are someone else    #
#  please comment with your initials                                     #
#----------------------------------------------------------------------- #

#--- IMPORT MODULES ---#
import time
from time import strftime
import random
import string
import xml.dom.minidom #<AA> xml parser module
from xml.dom.minidom import parse
import re #<AA> Regular expressions module... STAND BACK, I KNOW REGEX

#------------------------------------------------------------------------------------#
#<AA> Useful data

helptext="""\n
       ___                                        |` /
    _   |  |_   _   _                         _  --  _\\
   | |  |  | | |/  | |                       | |   \/
   | |  ,---.   7--' |  ,---. .---.   ,---..-' '-.
   | | / ,-. \\ / ,-. | / ,--' '--. | / ---''-. ,-'
   | | | | | | | | | | | |     ,-' | \\__ \\   | |
 _/  ' \\ `-' / \\ `-' | \\ `--. | <> | ,--' |  | `-.
|__,'   `---`   `--'-'  `---'  `---' `---'   `---'
\t\tWebpage Creator v4.0  by Stuart Lowe 
\t\tCreated: 21st April 2006
\t\tLast Updated: 25th November 2011\n
Create a directory for the issue in the archive dir. Put
all the MP3s there along with a .xml file with the same
name as the directory e.g. 200604.xml. You must also
include the path to this file in archive/shows.txt\n
usage: jodcastxml.py [-h] [--live [show.xml]] [--issue [YYYYMM, show.xml]]
                     [--current [show.xml]] [--rss [show.xml]]
                     [--archive [ARCHIVE]] [--search [SEARCH]]
                     [--nightsky [NIGHTSKY]] [--news [NEWS]] [--aaa [AAA]]\n"""


#------------------------------------------------------------------------------------#
#<AA> Function definitions


def message(mymessage):
    #<AA> Print time-stamped messages to the terminal <AA> stolen from the ALMA OST
    mytime = strftime("%Y-%m-%d %H:%M:%S")
    output_string = '[JOD '+mytime+']: '+mymessage
    print output_string


def checkLang(line_opts):
    #<AA> Checks if the user asked for a non english language with --lang input
    #<AA> if so set lang to equal user input, if not set to en for English.
    if line_opts['lang']:
        message('User specified Jodcast in '+str(line_opts['lang']))
        lang=line_opts['lang'][0]
        fileSuffix="_"+lang
    else:
        message('No language specified, making Jodcast in English')
        lang='en'
        fileSuffix=""

    return lang,fileSuffix

def jobsToDo(line_opts):
    #<AA> Takes commandline input and figures out which jobs you've asked it to
    #<AA> do. Prints them to screen and produces a to_do array for the main script.
    #<AA> The main script will check (using 'if' statements) whether or not to do
    #<AA> a particular job.

    to_do=[]

    for key in line_opts: #<AA> loops thru all possible arguments for this script
        if line_opts[key]: #<AA> if there is a value associated add to to_do
            message('Running \"'+key+'\" mode related tasks')

            to_do.append(key)

    return to_do

def genRandomName(issue):
    #<AA> Generates an 8 character string of random letters which will be unique to each
    #<AA> edition as the random seed is set each time it is run.
    random.seed(issue)
    randString=random.sample((string.lowercase[:25]+string.uppercase[:25]),8)
    randString="".join(randString)
    return randString

def getShows(archive,fileSuffix):
    #<AA> Gets a list of all the shows which exist ever from shows.txt in the archive on the
    #<AA> web machine ... shows.txt gets updated elsewhere
    f = open(archive+'shows.txt','r')
    files=[]
    for line in f:
        if fileSuffix != "": #<AA>If none english language selected change the line your looking for to contain the file suffix for that lang. 
            line=re.sub(".xml",fileSuffix+".xml", line)
        if line:
            files.append(line.rstrip('\n')) #<AA> the rstrip('\n') just removes the newline character from the end of the text
        
    f.close()
    return files


#<AA>-------------------------- PARSE XML AND WRITE HTML --------------------------------------#
#<AA> THIS IS A BIG, BIG FUNCTION! IT TAKES THE XML, GETS ALL THE RELEVANT SHOW INFO AND USES  #
#<AA> IT TO BUILD THE SHOW HTML................................................................#
#<AA> ANYONE WHO WANTS TO UNDERSTAND THIS SCRIPT NEEDS TO GET THEIR HEAD ROUND THIS AS IT DOES #
#<AA> MOST OF THE WORK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
def parseHTML(shownotes,showHTMLfile,fileSuffix):

    print shownotes
    DOMTree = xml.dom.minidom.parse(shownotes)
    theShow=DOMTree.documentElement

    #<AA> Proceed only if DOM Tree exists
    if theShow:
        #<AA> Get info about the whole show 
        #<AA> TITLE
        titleElems=theShow.getElementsByTagName("title")
    
        #<AA> for loop as there are many title tags in the XML, we only want 
        #<AA> the first which is the only one which has the sub attribute
        for title in titleElems:
            if title.hasAttribute("sub"):
                showTitle=title.childNodes[0].data
                showSubTitle=title.getAttribute("sub")
                print showTitle, showSubTitle

        #<AA> PUBLICATION DATE
        pubDateElem=theShow.getElementsByTagName("pubDate")[0]
        pubDate=pubDateElem.childNodes[0].data

        #<AA> ARCHIVE URL
        archiveElem=theShow.getElementsByTagName("archive")[0]
        archiveURL=archiveElem.getAttribute("url")
    
        #<AA> FORUM ID Do we even still use this?
        forumElem=theShow.getElementsByTagName("forum")[0]
        forumID=forumElem.getAttribute("id")

        #<AA> COPYRIGHT LINK
        copyrightElem=theShow.getElementsByTagName("copyright")[0]
        copyrightLink=copyrightElem.childNodes[0].data

        #<AA> MAIN KEYWORDS These should be the first listed in the XML
        #<AA> keywords for individual segments are read later
        showKeywordElem=theShow.getElementsByTagName("keywords")[0]
        showKeywords=showKeywordElem.childNodes[0].data
        print showKeywords
    
        #<AA> Get the preamble text for the webpage from XML
        showPreambleElem=theShow.getElementsByTagName('description')[0]
        showPreamble=showPreambleElem.childNodes[0].data
    
        #<AA> Get info on the show segments to build Body text
        interviewIndx=1
        segments=theShow.getElementsByTagName("segment")
        bodyHTML=""
        #<AA> Put page links into the show Preamble HMTL. This just swaps out chunks of the XML {type;text} with HTML
        preambleHTML=showPreamble
        preambleHTML=re.sub(r'\{',r'<a href="#', preambleHTML)
        preambleHTML=re.sub(r'\;',r'">', preambleHTML)
        preambleHTML=re.sub(r'\}',r'</a>' , preambleHTML)
        bodyHTML+=preambleHTML

        #<AA> Produce preamble with showtimes (for RSS??!?)
        #<AA> ... gets filled in in the segment for loop
        preambleST=showPreamble
    
        #<AA> loop through the many segments of the show
        for segment in segments:
            if segment.hasAttribute("type"):
                segType=segment.getAttribute("type")
                if segType=="interview":  #<AA> As there can be many interviews index them for page linking
                    segType=segType+str(interviewIndx)
                    interviewIndx=interviewIndx+1
                
                #<AA> Segment title and description information
                segTitleElem=segment.getElementsByTagName('title')[0]
                segTitle=segTitleElem.childNodes[0].data
                segDescElem=segment.getElementsByTagName('description')[0]
                segDesc=segDescElem.childNodes[0].data

                #<AA> Put above info in bodyHTML and create anchor links
                bodyHTML+="\n<a name=\""+segType+"\"></a><h2>"+segTitle+"</h2>"
                bodyHTML+="<p />"+segDesc+"\n"

                #<AA> Get segment start and end time
                segStartTimeElem=segment.getElementsByTagName('starttime')[0]
                segStartTime=segStartTimeElem.childNodes[0].data
                segEndTimeElem=segment.getElementsByTagName('endtime')[0]
                segEndTime=segEndTimeElem.childNodes[0].data
                segTimeString=" ["+segStartTime+"-"+segEndTime+"]"

                #<AA> Fill out preambleST. Sorry for the evil regex. Here is what it does
                #<AA> 1st) Matches and returns any none new line characters from the XML {type;text},
                #<AA> between the semi colon and the close curly bracket.
                #<AA> 2nd) Just tidies up the formatting of 1st
                #<AA> 3rd) replaces the "{type;" from the XML {type;text} with ""
                #<AA> 4th) replaces the "text}" from the XML {type;text} with "text [start-end]"
                preambleSTtags=re.search(re.escape(r"{"+segType+";")+"(.*?)"+re.escape(r"}"), preambleST) #<AA> 1st
                preambleSTWords=preambleSTtags.groups(1)[0]#<AA> 2nd
                preambleST=re.sub(r"{"+segType+";","", preambleST) #<AA> 3rd
                preambleST=re.sub(preambleSTWords+r'\}',preambleSTWords+segTimeString, preambleST) #<AA> 4th
    
        #<AA> Get authors
        authors=theShow.getElementsByTagName("author")
        authorHTML="<h2 id=\"showcredits\">Show Credits</h2>\n<table style=\"border:0px;\">\n"
        authorHTMLstart="<tr style=\"vertical-align:top;\"><td><b>"
        for author in authors:
            if author.hasAttribute("item"):
                authorHTML+=authorHTMLstart+author.getAttribute("item")+":</b></td><td>"+author.getAttribute("name")+"</td></tr>\n"

        authorHTML +="</table>\n<br />"
    
    #<AA> Read in HTML template
    tempHTML=open('template3.html','r')

    #<AA> Write XML shownote data to new HTML output
    showHTML=open(showHTMLfile,'w')
    for line in tempHTML:
        line=re.sub('<!-- TEMPLATE_PAGE_TITLE -->',showTitle+fileSuffix+" - show notes",line)#<AA> Sub in the show title
        line=re.sub('<!-- TEMPLATE_TITLE -->',showTitle,line)#<AA> Sub in the show title
        line=re.sub('<!-- TEMPLATE_SUBTITLE -->',": "+showSubTitle,line)#<AA> Sub in the show sub title
        line=re.sub('<!-- TEMPLATE_PUBDATE -->',pubDate,line)#<AA> Sub in the show publication date
        line=re.sub('<!-- TEMPLATE_BODY -->',bodyHTML,line)#<AA> Sub in the show body (blank to begin with)
        line=re.sub('<!-- TEMPLATE_AUTHORS -->',authorHTML,line)#<AA> Sub in the Author info
        print >> showHTML, line #<AA> Print to output HTML

