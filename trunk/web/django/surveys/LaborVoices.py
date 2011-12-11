import os, sys, csv
from datetime import datetime, timedelta
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call
from otalo.AO.models import Line
import otalo_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
PREFIX='freetdm/grp1/a/0'
SUFFIX=''
SOUND_EXT = ".wav"
BARGEIN_KEY='9'
LV_ORIG_LINEID=1

'''
****************************************************************************
******************* SURVEY GENERATION ****************************************
****************************************************************************
'''
def create_survey(subdir, number, callback=False, inbound=False, template=False):
    s = Survey.objects.filter(name='LV_'+subdir+'_SURVEY', number=number, callback=callback, inbound=inbound, template=template)
    if bool(s):
        s = s[0]
        s.delete()
    s = Survey(name='LV_'+subdir+'_SURVEY', number=number, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=0, callback=callback, inbound=inbound, template=template)
    s.save()    
    
    order = 1
    
    welcome = Prompt(file=subdir+"welcome_survey"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    welcome.save()
    welcome_opt = Option(number="1", action=Option.INPUT, prompt=welcome)
    welcome_opt.save()
    welcome_opt2 = Option(number="2", action=Option.INPUT, prompt=welcome)
    welcome_opt2.save()
    welcome_opt3 = Option(number="3", action=Option.INPUT, prompt=welcome)
    welcome_opt3.save()
    order+=1
    
    survey = Prompt(file=subdir+"survey"+SOUND_EXT, order=order, survey=s, delay=0, bargein=True)
    survey.save()
    survey_opt = Option(number="", action=Option.NEXT, prompt=survey)
    survey_opt.save()
    survey_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=survey)
    survey_opt2.save()
    order+=1
    
    factory = Prompt(file=subdir+"factory"+SOUND_EXT, order=order, survey=s, name="Factory")
    factory.save()
    record_opt = Option(number="", action=Option.RECORD, prompt=factory)
    record_opt.save()
    order+=1
    
    working_hours = Prompt(file=subdir+"working_hours"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    working_hours.save()
    working_hours_opt = Option(number="1", action=Option.INPUT, prompt=working_hours)
    working_hours_opt.save()
    working_hours_opt2 = Option(number="2", action=Option.INPUT, prompt=working_hours)
    working_hours_opt2.save()
    working_hours_opt3 = Option(number="3", action=Option.INPUT, prompt=working_hours)
    working_hours_opt3.save()
    working_hours_opt4 = Option(number="4", action=Option.INPUT, prompt=working_hours)
    working_hours_opt4.save()
    order+= 1
    
    min_wage = Prompt(file=subdir+"minimum_wage"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    min_wage.save()
    min_wage_opt = Option(number="1", action=Option.INPUT, prompt=min_wage)
    min_wage_opt.save()
    min_wage_opt2 = Option(number="2", action=Option.INPUT, prompt=min_wage)
    min_wage_opt2.save()
    min_wage_opt3 = Option(number="3", action=Option.INPUT, prompt=min_wage)
    min_wage_opt3.save()
    min_wage_opt4 = Option(number="4", action=Option.INPUT, prompt=min_wage)
    min_wage_opt4.save()
    order+= 1
    
    overtime_hours = Prompt(file=subdir+"overtime_hours"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    overtime_hours.save()
    overtime_hours_opt = Option(number="1", action=Option.INPUT, prompt=overtime_hours)
    overtime_hours_opt.save()
    overtime_hours_opt2 = Option(number="2", action=Option.INPUT, prompt=overtime_hours)
    overtime_hours_opt2.save()
    overtime_hours_opt3 = Option(number="3", action=Option.INPUT, prompt=overtime_hours)
    overtime_hours_opt3.save()
    order+= 1
    
    overtime_wages = Prompt(file=subdir+"overtime_wages"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    overtime_wages.save()
    overtime_wages_opt = Option(number="1", action=Option.INPUT, prompt=overtime_wages)
    overtime_wages_opt.save()
    overtime_wages_opt2 = Option(number="2", action=Option.INPUT, prompt=overtime_wages)
    overtime_wages_opt2.save()
    order+= 1
    
    harassment = Prompt(file=subdir+"harassment"+SOUND_EXT, order=order, survey=s, name='Harassment')
    harassment.save()
    record_opt = Option(number="", action=Option.RECORD, prompt=harassment)
    record_opt.save()
    order+=1
    
    brand = Prompt(file=subdir+"brand"+SOUND_EXT, order=order, survey=s, name='Brand')
    brand.save()
    record_opt = Option(number="", action=Option.RECORD, prompt=brand)
    record_opt.save()
    order+=1
    
    thankyou = Prompt(file=subdir+"thankyou_survey"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    thankyou.save()
    thankyou_opt = Option(number="", action=Option.GOTO, prompt=thankyou)
    thankyou_opt.save()
    order+=1
    
    disconnect_future = Prompt(file=subdir+"disconnect_future"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    disconnect_future.save()
    disconnect_future_opt = Option(number="", action=Option.GOTO, prompt=disconnect_future)
    disconnect_future_opt.save()
    
    param = Param(option=welcome_opt2, name=Param.IDX, value=order)
    param.save()
    order+=1
    
    disconnect_remove = Prompt(file=subdir+"disconnect_remove"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    disconnect_remove.save()
    disconnect_remove_opt = Option(number="", action=Option.GOTO, prompt=disconnect_remove)
    disconnect_remove_opt.save()
    
    param = Param(option=welcome_opt3, name=Param.IDX, value=order)
    param.save()
    order+=1
    
    param = Param(option=thankyou_opt, name=Param.IDX, value=order)
    param.save()
    
    param = Param(option=disconnect_future_opt, name=Param.IDX, value=order)
    param.save()
    
    param = Param(option=disconnect_remove_opt, name=Param.IDX, value=order)
    param.save()
        
    return s

'''
****************************************************************************
******************* MAIN ***************************************************
****************************************************************************
'''
def main():
    '''
    For the Demo lines, the forums are shared. So just associate the bcast
    template with the first of the shared forums (reverse engineering the
    algorithm used to get the templates in regularbcast)
    '''
    l = Line.objects.get(pk=LV_ORIG_LINEID)
    forums = l.forums.all()
    f = forums[0]
    l = f.line_set.all()[0]
    num = l.number
    if l.outbound_number:
        num = l.outbound_number
    create_survey('kan',num,template=True)
    create_survey('lveng',num,template=True)
    
    # next create inbound surveys
    create_survey('lveng','7961907780',callback=True, inbound=True)
    create_survey('lveng','7961907781',inbound=True)
    create_survey('kan','7961907782',callback=True, inbound=True)
    create_survey('kan','7961907783',inbound=True)

main()