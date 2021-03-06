#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: lecorguille@sb-roscoff.fr
#
#
# This programme can duplicate tool within the tools panel
# It take a tool_list.yaml with a new element list tool_panel_section_id_alts
#         - name: anova
#           owner: lecorguille
#           tool_panel_section_id: 'LCMS-statistical_analysis'
#           tool_panel_section_id_alts: 
#             - 'LCMS-statistical_analysis'
#             - 'GCMS-statistical_analysis'
#             - 'NMR-statistical_analysis'
# and a shed_tool_conf.xml file
#
# NOTE that this program can't deal with different chanset_revision
#


from xml.dom import minidom
from re import sub
import yaml
import argparse
import shutil

def getTools(xmldoc):
    tools={}

    for sectionElement in xmldoc.getElementsByTagName('section'):
        for toolElement in sectionElement.getElementsByTagName('tool'):
            # <tool file="toolshed.g2.bx.psu.edu/repos/lecorguille/anova/bcd05315efc5/anova/abims_anova.xml" guid="toolshed.g2.bx.psu.edu/repos/lecorguille/anova/abims_anova/1.1.4">
            #     <tool_shed>toolshed.g2.bx.psu.edu</tool_shed>
            #     <repository_name>anova</repository_name>
            #     <repository_owner>lecorguille</repository_owner>
            #     <installed_changeset_revision>bcd05315efc5</installed_changeset_revision>
            #     <id>toolshed.g2.bx.psu.edu/repos/lecorguille/anova/abims_anova/1.1.4</id>
            #     <version>1.1.4</version>
            # </tool>
            
            toolId = toolElement.getElementsByTagName('tool_shed')[0].firstChild.nodeValue+"/"+toolElement.getElementsByTagName('repository_owner')[0].firstChild.nodeValue+"/"+toolElement.getElementsByTagName('repository_name')[0].firstChild.nodeValue
            #toolIdRevision = toolId+"/"+toolElement.getElementsByTagName('installed_changeset_revision')[0].firstChild.nodeValue
            if not (tools.has_key(toolId)):
                #tools[toolIdRevision] = {'xmlelements' : [], 'section' : sectionElement.getAttribute('id')}
                tools[toolId] = {'xmlelements' : [], 'section' : sectionElement.getAttribute('id')}
            #tools[toolIdRevision]['xmlelements'].append(toolElement)
            tools[toolId]['xmlelements'].append(toolElement)

    return tools
    

def addToolInSection(xmldoc,xmltool,tool_panel_section_id_alt):
    
    for toolElement in xmltool["xmlelements"]:
        sectionElement = xmldoc.createElement("section")
        sectionElement.setAttribute("id",tool_panel_section_id_alt)

        toolElementNew = toolElement.cloneNode(True)
        sectionElement.appendChild(toolElementNew)

        xmldoc.getElementsByTagName('toolbox')[0].appendChild(sectionElement)

    return xmldoc

if __name__ == '__main__':
    # Arguments
    parser = argparse.ArgumentParser(description='This script will duplicate the tool within the tool panel accroding to a tool_list.yaml and its tags tool_panel_section_id_alts')
    parser.add_argument('tool_list', metavar='tool_list', type=argparse.FileType('r'), help='a tool_list.yaml')
    parser.add_argument('shed_tool_conf', metavar='shed_tool_conf', type=argparse.FileType('r'), help='a shed_tool_conf.xml')
    parser.add_argument("-i",dest="replace",help="Edit files in place",action="store_true",default=False)

    args = parser.parse_args()
    
    # parsing
    xmldoc = minidom.parse(args.shed_tool_conf)
    xmltools = getTools(xmldoc)

    yamldoc = yaml.load(args.tool_list)


    # browse yaml to get tools which need alternative section
    for yamltool in yamldoc['tools']:
        # - name: anova
        #   owner: lecorguille
        #   tool_panel_section_id: 'LCMS-statistical_analysis'
        #   tool_panel_section_id_alts: 
        #     - 'LCMS-statistical_analysis'
        #     - 'GCMS-statistical_analysis'
        #     - 'NMR-statistical_analysis'
        
        if (yamltool.has_key('tool_panel_section_id_alts')):
            yamltoolId = sub('http[s]?://', r'', yamltool['tool_shed_url'])+"/"+yamltool['owner']+"/"+yamltool['name']
            #@TODO: deal with revisions (note that its a list too)
            #yamltoolId = yamltoolId+"/"+tool['revisions']
            xmltool = xmltools[yamltoolId]
            for tool_panel_section_id_alt in yamltool['tool_panel_section_id_alts']:
                if (tool_panel_section_id_alt == xmltool['section']):
                    continue
                print ("adding "+yamltoolId+" in "+tool_panel_section_id_alt)
                xmldoc = addToolInSection(xmldoc,xmltool,tool_panel_section_id_alt)

    # write the modify xml
    if args.replace is False :
        outputFilename = args.shed_tool_conf.name+".new"
    else:
        shutil.copy2(args.shed_tool_conf.name, args.shed_tool_conf.name+".noduplicate")
        outputFilename = args.shed_tool_conf.name
    outfd=open(outputFilename,"w")
    xmldoc.writexml(outfd,addindent="  ",newl="\n")





