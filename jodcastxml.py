#------------------------------------------------------------------------#
#  An attempt to write the import Jodcast code in Python rather than Perl#
#  Created by Adam Avison 22/01/2015                                     #
#  Comments starting <AA> were written by me. If you are someone else    #
#  please comment with your initials                                     #
#----------------------------------------------------------------------- #

#--- IMPORT MODULES ---#
import sys #<AA> import system functionality
import os #<AA> import operating system functionality
import re #<AA> import regex capability
import argparse #<AA> import commandline argument processing module
from argparse import RawTextHelpFormatter #<AA> Imported to make helptext show multiple lines
from jodcastxml_helper import * #<AA> Contains useful functions etc.

#--- DIRECTORY INFO ---#
#jodcastDir="/local/scratch/jodcast_backup/jodcast_1/jodcast/raw/"
#baseWebDir="/home/www/public_html/jodcast/archive/"
jodcastDir="/Users/aavison/Documents/Jodcast/NewCode/hodcast/"
baseWebDir="/Users/aavison/Documents/Jodcast/NewCode/fakeweb/"

#------------------------------------------------------------------------#
#<AA> This section allows command line functionality for this script
#<AA> Usage: python jodcastxml.py --build <option>

inp_parser=argparse.ArgumentParser(description=helptext, formatter_class=RawTextHelpFormatter)
inp_parser.add_argument('--live', help='does things to make show live', const='do_live', action='store_const')

inp_parser.add_argument('--issue', type=str, help='generates temporary shownotes. Needs YYYYMM option', nargs=2, metavar=('[YYYYMM,','show.xml]'))

inp_parser.add_argument('--current', type=str, help='update the inc/current.txt and .htaccess file', nargs='?', metavar='show.xml')

inp_parser.add_argument('--rss', help='to rebuild RSS feed', const='do_rss', action='store_const')

inp_parser.add_argument('--archive', help='to rebuild archive page', const='do_archive', action='store_const')

inp_parser.add_argument('--search', help='to rebuild search databases', const='do_search', action='store_const')

inp_parser.add_argument('--nightsky', help='to rebuild the night sky special section', const='do_nightsky', action='store_const')

inp_parser.add_argument('--news', help='to rebuild the news special section', const='do_news', action='store_const')

inp_parser.add_argument('--aaa', help='to rebuild the ask an astronomer special section', const='do_aaa', action='store_const')

inp_parser.add_argument('--lang', help='as issue, but in different lang', type=str, nargs=1)

args = inp_parser.parse_args()

line_opts=vars(args)

#-------------------------------------------------------------------------#
#<AA> Figure out what has been asked for on commandline input and
#<AA> print to screen

language,langFileSuffix=checkLang(line_opts) #<AA> Check if a none English language was asked for and set language variable and language file suffix

toDoList=jobsToDo(line_opts) #<AA> Check commandline input & create a 'to Do' list of jobs which need doing

#-------------------------------------------------------------------------#
#<AA> The 'if' statements below check the toDoList and if a certain job is
#<AA> in the toDoList they run the code required to complete that job.

"""<AA> Break down of the various modes which can be selected

ISSUE MODE: This mode is the initial setup of the directory structure for a given YYYYMM(Extra) show
            on the web side of things. It refers to thinks on the jodcast machine side of things.
            This needs user to input a YYYYMM for that show.
            Check to see if the YYYYMM web directory exists, if not puts all
            If YYYYMM doesn't start with a date, the code assumes its a video and points at the *_video directory 
            

"""

if 'issue' in toDoList:
    #<AA> Get the issue name from command line input
    issueName=line_opts['issue'][0]
    
    #<AA> Define output web directory. If the 'final' YYYYMM directory exists on the web machine point at that, 
    #<AA> if not generate random string and point at that.
    if os.path.isdir(baseWebDir+issueName):
        message(baseWebDir+str(issueName)+' exists')
        baseFile=baseWebDir+str(issueName)+'/'
        message('Web output directory at:\n '+baseFile+'')
        webDirExists=True
    else:
        message(baseWebDir+str(issueName)+' does not exists')
        message('Generating random string directory location')
        randFold=genRandomName(issueName)
        baseFile=baseWebDir+randFold+'/'
        message('Web output directory at:\n '+baseFile+'')
        webDirExists=False
        
    #<AA> Define the location of the XML file containing the shownotes.
    showNotesLoc=baseFile+issueName+langFileSuffix+".xml"
    message("The shownotes should be here:\n "+showNotesLoc)

    #<AA> Check if those shownotes exist in that location (on web machine).
    #<AA> If not change showNotesLoc to Jodcast machine rather than web machine and check there.
    if os.path.isfile(showNotesLoc):
        message("Good the shownotes should are here:\n "+showNotesLoc)
    else:
        message("The shownotes are not here:\n "+showNotesLoc)
        message("Now checking Jodcast machine for shownotes")
        jodShowNotesLoc=jodcastDir+issueName+langFileSuffix+".xml"
        #<AA> Check the XML is on the Jodcast Machine
        if os.path.isfile(jodShowNotesLoc):
            message("OK using these shownotes on the Jodcast Machine instead:\n"+jodShowNotesLoc)
            showNotesLoc=jodShowNotesLoc
        else:
            message("No XML at:\n"+jodShowNotesLoc)
            message("Exiting this script, get some XML!")
            sys.exit()
            
        
    #<AA> Define where to save the shownotes to HTML.
    #<AA> If we are using the 'final' directory save shownotes to index2.html
    #<AA> If we are using random string directory save shownotes to index.html overwriting old version
    finalHTML=baseFile+"index"+langFileSuffix+".html"
    
    if webDirExists:
        previewHTML=baseFile+"index"+langFileSuffix+"2.html"
        message("Will write shownotes to:\n "+previewHTML)
        message("Don't forget to move to index.html for release!")
    else:
        previewHTML=finalHTML
        message("Will write shownotes to:\n"+previewHTML)

    #<AA> Now that we know where the shownotes XML is and where we'll be writing it to...
    #<AA> Lets parse the shownotes into HTML.
    parseHTML(showNotesLoc,previewHTML,langFileSuffix)


#------- SOMETHING ---------------------#
#<AA> THIS ONLY GETS DONE IF MODE==LIVE
    
if 'live' in toDoList:
    showFiles=getShows(baseWebDir,langFileSuffix)
    print showFiles

    
