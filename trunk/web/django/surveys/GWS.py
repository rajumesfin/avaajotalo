import os, sys, csv, re, shutil
from datetime import datetime, timedelta
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call, Input
import otalo_utils

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
OUTPUT_FILE_DIR='/home/gws/reports/'
PREFIX='freetdm/grp5/a/'
SUFFIX=''
SUBDIR = 'gws/'
SOUND_EXT = ".wav"
REPEAT_KEY='*'
BARGEIN_KEY='9'

'''
****************************************************************************
******************* SURVEY GENERATION ****************************************
****************************************************************************
'''
def create_survey(prefix, language, options, phone_num, callback, inbound, template=False, includeid=False, countrycode = '0'):
    s = Survey(name='GWS_'+prefix+'_'+language, number=phone_num, dialstring_prefix=PREFIX+countrycode, dialstring_suffix=SUFFIX, complete_after=0, callback=callback, inbound=inbound, template=template)
    s.save()
    print('creating new survey '+str(s))
    
    order = 1
    if includeid:
        id = Prompt(file=SUBDIR+language+'/'+prefix+"id"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000, inputlen=4)
        id.save()
        order += 1
    
    intro = Prompt(file=SUBDIR+language+'/'+prefix+"intro"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    intro.save()
    intro_opt = Option(number="", action=Option.NEXT, prompt=intro)
    intro_opt.save()
    intro_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=intro)
    intro_opt2.save()
    order += 1
    
    for i in range(len(options)):
        p = Prompt(file=SUBDIR+language+'/'+prefix+str(i+1)+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
        p.save()
        opts = options[i]
        if '*' in opts:
            # input length (assume single digit)
            p.inputlen = int(opts[1:2])
            p.save()
        elif 'rec' in opts:
            p.name = opts[opts.find('rec')+3:]
            p.delay = 2000
            p.bargein=False
            p.save()
            record_opt = Option(number="", action=Option.RECORD, prompt=p)
            record_opt.save()
            param = Param(option=record_opt, name=Param.CONFIRM_REC, value="0")
            param.save()
            param2 = Param(option=record_opt, name=Param.MAXLENGTH, value="15")
            param2.save()
        else:
            maxopt = int(opts)
            for j in range(1,maxopt+1):
                p_opt = Option(number=str(j), action=Option.INPUT, prompt=p)
                p_opt.save()
        if 'dep' in opts:
            dependson = opts[opts.find('d')+3:]
            # assume it is index for a question number
            dependson = int(dependson)+1
            if includeid:
                dependson += 1
            # assume it depends on an earlier prompt
            p.dependson = Prompt.objects.get(survey=s,order=dependson)
            # remove the SOUND_EXT and add hyphen
            p.file = p.file[:p.file.find(SOUND_EXT)] + '-'
            p.save()
        repeat = Option(number=REPEAT_KEY, action=Option.REPLAY, prompt=p)
        repeat.save()
        order+=1
    
    outro = Prompt(file=SUBDIR+language+'/'+prefix+"outro"+SOUND_EXT, order=order, bargein=True, survey=s, delay=2000)
    outro.save()
    outro_opt = Option(number="", action=Option.NEXT, prompt=outro)
    outro_opt.save()
    outro_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=outro)
    outro_opt2.save()
    order += 1
    
    return s

def create_intl_test_survey(phone_num, callback=False, inbound=False, template=False):
    s = Survey.objects.filter(name='GWS_INTL', number=phone_num, callback=callback, inbound=inbound, template=template)
    if bool(s):
        s = s[0]
        s.delete()
        print('deleting survey')
    s = Survey(name='GWS_INTL', number=phone_num, dialstring_prefix=PREFIX, dialstring_suffix=SUFFIX, complete_after=1, callback=callback, inbound=inbound, template=template)
    s.save()
    print('creating new survey '+str(s))

        
    order = 1
    intro = Prompt(file=SUBDIR+"eng/efintro"+SOUND_EXT, order=order, bargein=True, survey=s, delay=0)
    intro.save()
    intro_opt = Option(number="", action=Option.NEXT, prompt=intro)
    intro_opt.save()
    intro_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=intro)
    intro_opt2.save()
    order += 1
    
    q1 = Prompt(file=SUBDIR+"eng/ef1"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    q1.save()
    q1_opt = Option(number="1", action=Option.INPUT, prompt=q1)
    q1_opt.save()
    q1_opt2 = Option(number="2", action=Option.INPUT, prompt=q1)
    q1_opt2.save()
    order+=1
    
    q2 = Prompt(file=SUBDIR+"eng/ef5"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    q2.save()
    q2_opt = Option(number="1", action=Option.INPUT, prompt=q2)
    q2_opt.save()
    q2_opt2 = Option(number="2", action=Option.INPUT, prompt=q2)
    q2_opt2.save()
    q2_opt3 = Option(number="3", action=Option.INPUT, prompt=q2)
    q2_opt3.save()
    order+=1
    
    q3 = Prompt(file=SUBDIR+"eng/ef10"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000)
    q3.save()
    q3_opt = Option(number="1", action=Option.INPUT, prompt=q3)
    q3_opt.save()
    q3_opt2 = Option(number="2", action=Option.INPUT, prompt=q3)
    q3_opt2.save()
    q3_opt3 = Option(number="3", action=Option.INPUT, prompt=q3)
    q3_opt3.save()
    order+=1
    
    q4 = Prompt(file=SUBDIR+"eng/intl4"+SOUND_EXT, order=order, bargein=True, survey=s, delay=4000, inputlen=10)
    q4.save()
    #q4_opt = Option(number="1", action=Option.INPUT, prompt=q4)
    #q4_opt.save()
    #q4_opt2 = Option(number="2", action=Option.INPUT, prompt=q4)
    #q4_opt2.save()
    #q4_opt3 = Option(number="3", action=Option.INPUT, prompt=q4)
    #q4_opt3.save()
    #q4_opt4 = Option(number="4", action=Option.INPUT, prompt=q4)
    #q4_opt4.save()
    #q4_opt5 = Option(number="5", action=Option.INPUT, prompt=q4)
    #q4_opt5.save()
    #q4_opt6 = Option(number="6", action=Option.INPUT, prompt=q4)
    #q4_opt6.save()
    #q4_opt7 = Option(number="7", action=Option.INPUT, prompt=q4)
    #q4_opt7.save()
    #q4_opt8 = Option(number="8", action=Option.INPUT, prompt=q4)
    #q4_opt8.save()
    #q4_opt9 = Option(number="9", action=Option.INPUT, prompt=q4)
    #q4_opt9.save()
    order+=1
     
    outro = Prompt(file=SUBDIR+"eng/efoutro"+SOUND_EXT, order=order, bargein=True, survey=s, delay=2000)
    outro.save()
    outro_opt = Option(number="", action=Option.NEXT, prompt=outro)
    outro_opt.save()
    outro_opt2 = Option(number=BARGEIN_KEY, action=Option.NEXT, prompt=outro)
    outro_opt2.save()
    order += 1
        
    return s

'''
****************************************************************************
******************* REPORTING **********************************************
****************************************************************************
'''
        
def survey_results(number, filename, phone_num_filter=False, date_start=False, date_end=False):
    all_calls = []
    open_calls = {}
    soundfiles = {}
    survey = Survey.objects.filter(number=number, inbound=True)[0]
    
    f = open(filename)

    while(True):
        line = f.readline()
        if not line:
            break
        try:
        
        #################################################
        ## Use the calls here to determine what pieces
        ## of data must exist for the line to be valid.
        ## All of those below should probably always be.
        
            phone_num = otalo_utils.get_phone_num(line)
            current_date = otalo_utils.get_date(line)        
            dest = otalo_utils.get_destination(line)            
        ##
        ################################################
            
            if phone_num_filter and not phone_num in phone_num_filter:
                continue
                
            if date_start:
                if date_end:
                    if not (current_date >= date_start and current_date < date_end):
                        continue
                    if current_date > date_end:
                        break
                else:
                    if not current_date >= date_start:
                        continue
    
            if line.find("Start call") != -1:
                # check to see if this caller already has one open
                if phone_num in open_calls:
                    # close out call                
                    open_call = open_calls[phone_num]    
                    start = open_call['start']
                    dur = current_date - start
                    call = Call.objects.filter(subject__number=phone_num, date__gte=start-timedelta(seconds=40), date__lte=start+timedelta(seconds=40), complete=True)
                    if bool(call):
                        #if call.count()>1:
                            #print("more than one call found: " + str(call))
                        call = call[0]
                        result = [call.subject.number, time_str(call.date), str(dur.seconds)]
        
                        inputs = Input.objects.select_related(depth=1).filter(call=call).order_by('id')
                        callerid = inputs.filter(prompt__file__contains="id"+SOUND_EXT)
                        if bool(callerid):
                            callerid = callerid[0].input
                        
                        for input in inputs:
                            if '.mp3' in input.input:
                                if callerid:
                                    if callerid in soundfiles:
                                        soundfiles[callerid].append(input.input)
                                        fname = callerid + "-" + str(len(soundfiles[callerid])) + '.mp3'
                                        result.append(fname)
                                    else:
                                        soundfiles[callerid] = [input.input]
                                        result.append(callerid + ".mp3")
                                else:
                                    # complicated in order to keep file copy 
                                    # code consistent down below.
                                    soundfiles[input.input[:-4]] = [input.input]
                                    result.append(input.input)
                            else:
                                result.append(input.input)                         
                        all_calls.append(result)
                    #else:
                        #print("no call found: num=" +phone_num+ ";sessid ="+ otalo_utils.get_sessid(line)+ ";start="+start.strftime('%m-%d-%y %H:%M:%S'))
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
                open_calls[phone_num] = {'start':current_date}
                
            elif line.find("End call") != -1 or line.find("Abort call") != -1:
                if phone_num in open_calls:
                    open_call = open_calls[phone_num]    
                    start = open_call['start']
                    dur = current_date - start
                    call = Call.objects.filter(subject__number=phone_num, date__gte=start-timedelta(seconds=40), date__lte=start+timedelta(seconds=40), complete=True)
                    if bool(call):
                        call = call[0]
                        result = [call.subject.number, time_str(call.date), str(dur.seconds)]
        
                        inputs = Input.objects.select_related(depth=1).filter(call=call).order_by('id')
                        callerid = inputs.filter(prompt__file__contains="id"+SOUND_EXT)
                        if bool(callerid):
                            callerid = callerid[0].input
                        
                        for input in inputs:
                            if '.mp3' in input.input:
                                if callerid:
                                    if callerid in soundfiles:
                                        soundfiles[callerid].append(input.input)
                                        fname = callerid + "-" + str(len(soundfiles[callerid])) + '.mp3'
                                        result.append(fname)
                                    else:
                                        soundfiles[callerid] = [input.input]
                                        result.append(callerid + ".mp3")
                                else:
                                    # complicated in order to keep file copy 
                                    # code consistent down below.
                                    soundfiles[input.input[:-4]] = [input.input]
                                    result.append(input.input)
                            else:
                                result.append(input.input)                         
                        all_calls.append(result)
                    #else:
                        #print("no call found: num=" +phone_num+ ";sessid ="+ otalo_utils.get_sessid(line)+ ";start="+start.strftime('%m-%d-%y %H:%M:%S'))
                    del open_calls[phone_num]
                    
        except KeyError as err:
            #print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
            raise
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
    
    header = ['number','start','duration (s)']
    qcount = Prompt.objects.filter(survey=survey).exclude(file__contains='intro').exclude(file__contains='outro').count()
    for i in range(1,qcount+1):
        header.append('q'+str(i))
    outputfilename='survey_results_'+number
    audiofile_dir = 'audio_'+number
    if date_start:
        outputfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
        audiofile_dir+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
    audiofile_dir += "/"
    outputfilename = OUTPUT_FILE_DIR+outputfilename+'.csv'
    output = csv.writer(open(outputfilename, 'wb'))
    output.writerow(header)            
    output.writerows(all_calls)
    
    if len(soundfiles) > 0:
        if os.path.isdir(OUTPUT_FILE_DIR+audiofile_dir):
            shutil.rmtree(OUTPUT_FILE_DIR+audiofile_dir)
        os.mkdir(OUTPUT_FILE_DIR+audiofile_dir)
        for callid,files in soundfiles.items():
            for i in range(len(files)):
                f = files[i]
                fname = callid + '.mp3'
                if i > 0:
                    fname = callid + "-" + str(i+1) + '.mp3'
                shutil.copy(settings.MEDIA_ROOT+'/'+f, OUTPUT_FILE_DIR+audiofile_dir+fname)
    
def repeats_requests(filename, phone_num_filter=False, date_start=False, date_end=False):
    repeat_counts = {}
    open_calls = {}
    
    f = open(filename)

    while(True):
        line = f.readline()
        if not line:
            break
        try:
        
        #################################################
        ## Use the calls here to determine what pieces
        ## of data must exist for the line to be valid.
        ## All of those below should probably always be.
        
            phone_num = otalo_utils.get_phone_num(line)
            current_date = otalo_utils.get_date(line)        
            dest = otalo_utils.get_destination(line)            
        ##
        ################################################
            
            if phone_num_filter and not phone_num in phone_num_filter:
                continue
                
            if date_start:
                if date_end:
                    if not (current_date >= date_start and current_date < date_end):
                        continue
                    if current_date > date_end:
                        break
                else:
                    if not current_date >= date_start:
                        continue
    
            if line.find("Start call") != -1:
                # check to see if this caller already has one open
                if phone_num in open_calls:
                    # close out call                
                    totcounts = open_calls[phone_num]['total']  
                    starcounts = open_calls[phone_num]['*']
                    for prompt in totcounts:
                        tot = totcounts[prompt]
                        stars = 0
                        if prompt in starcounts:
                            stars = starcounts[prompt]
                        
                        if prompt not in repeat_counts:
                            repeat_counts[prompt] = [stars, tot-stars]
                        else:
                            repeat_counts[prompt][0] += stars
                            repeat_counts[prompt][1] += tot-stars
                    
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
                open_calls[phone_num] = {'total':{}, '*':{}}
                
            elif line.find("End call") != -1 or line.find("Abort call") != -1:
                if phone_num in open_calls:
                    # close out call                
                    totcounts = open_calls[phone_num]['total']  
                    starcounts = open_calls[phone_num]['*']
                    for prompt in totcounts:
                        tot = totcounts[prompt]
                        stars = 0
                        if prompt in starcounts:
                            stars = starcounts[prompt]
                        
                        if prompt not in repeat_counts:
                            repeat_counts[prompt] = [stars, tot-stars]
                        else:
                            repeat_counts[prompt][0] += stars
                            repeat_counts[prompt][1] += tot-stars
                    
                    del open_calls[phone_num]
                    
            if phone_num in open_calls and line.find("dtmf") != -1 and line.find("*") != -1:
                counts = open_calls[phone_num]['*']
                prompt = line[line.rfind('/')+1:line.find('.wav')]
                if prompt not in counts:
                    counts[prompt] = 1
                else:
                    counts[prompt] += 1
            elif phone_num in open_calls and otalo_utils.is_prompt(line):
                counts = open_calls[phone_num]['total']
                prompt = line[line.rfind('/')+1:line.find('.wav')]
                if prompt not in counts:
                    counts[prompt] = 0
                else:
		    #if 'intro' in prompt or 'outro' in prompt:
			#print(line)
                    counts[prompt] += 1
                    
        except KeyError as err:
            #print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
            raise
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
    
    header = ['prompt','star presses', 'no input']
    outputfilename='repeats_79'+filename[filename.rfind('_')+1:filename.find('.log')]
    if date_start:
        outputfilename+='_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]
    outputfilename = OUTPUT_FILE_DIR+outputfilename+'.csv'
    output = csv.writer(open(outputfilename, 'wb'))
    output.writerow(header)
    prompts = repeat_counts.keys()
    prompts = natural_sorted(prompts)
    for prompt in prompts:                    
        output.writerow([prompt]+repeat_counts[prompt])
    

'''
****************************************************************************
******************* UTILS **************************************************
****************************************************************************
'''
def time_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')

def natural_sorted( l ): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


'''
****************************************************************************
******************* MAIN ***************************************************
****************************************************************************
'''
def main():
    if '--weeklyreports' in sys.argv:
        number = sys.argv[2]    
        filename = settings.LOG_ROOT + 'survey_in_'+ number[-8:] + '.log'
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        start = today-timedelta(days=6)
        survey_results(number, filename, date_start=start)
        repeats_requests(filename, date_start=start)
    elif '--report' in sys.argv or '--repeats' in sys.argv:
        number = sys.argv[2]    
        filename = settings.LOG_ROOT + 'survey_in_'+ number[-8:] + '.log'
        start=None  
        if len(sys.argv) > 3:
            start = datetime.strptime(sys.argv[3], "%m-%d-%Y")
        end = None    
        if len(sys.argv) > 4:
            end = datetime.strptime(sys.argv[4], "%m-%d-%Y")
        if '--report' in sys.argv:
            survey_results(number, filename, date_start=start, date_end=end)
        else:
            repeats_requests(filename, date_start=start, date_end=end)
              
    #else:
        #create_survey('ppi', 'pun', ['2','*1','3','2','4','2','2','2','2','*1','*1','*2'], '7961555076', callback=True, inbound=True)
        #create_survey('ppi', 'hin', ['2','*1','3','2','4','2','2','2','2','*1','*1','*2'], '7961555078', callback=True, inbound=True)
        #create_survey('ppi', 'kan', ['2','*1','3','2','4','2','2','2','2','*1','*1','*2'], '7961555095', callback=True, inbound=True)
        #create_survey('ppi', 'tam', ['2','*1','3','2','4','2','2','2','2','*1','*1','*2'], '7961555097', callback=True, inbound=True)
        
        #create_survey('ef', 'eng', ['2','*1','4','2','3','3','3','3','2','3','6'], '7961555000', callback=True, inbound=True)
        
	    #create_survey('sa', 'hin', ['2','*2','3','3','3','2','3','3','2','2','2','2','2'], '7961555015', callback=True, inbound=True)
        #create_survey('sa', 'eng', ['2','*2','3','3','3','2','3','3','2','2','2','2','2'], '7961555002', callback=True, inbound=True)
        
        #create_survey('lw', 'tam', ['*1','4','6','3','2','*5','2','3','3','4','*2','5'], '7961555004', callback=True, inbound=True)
        #create_survey('lw', 'eng', ['*1','4','6','3','2','*5','2','3','3','4','*2','5'], '7961555001', callback=True, inbound=True)
        
        #create_survey('artisan', 'eng', ['2','*1','3','4','3','3','5','3','3','3','3'], '7961555003', callback=True, inbound=True)
        #create_intl_test_survey('7961555006')
        #create_intl_test_survey('7961555007', inbound=True, callback=True)
        #create_survey('', 'tiru/hinA', ['3','2','2','4','5','*2','*2','5','3','reccomp','2','2','*3dep12'], '7961555032', callback=True, inbound=True, includesid=True)
        #create_survey('', 'tiru/hinB', ['3','2','2','4','5','*2','*2','5','3','recbrands','2','2','*3dep12'], '7961555034', callback=True, inbound=True, includesid=True)
        #create_survey('', 'tiru/tamA', ['3','2','2','4','5','*2','*2','5','3','reccomp','2','2','*3dep12'], '7961555021', callback=True, inbound=True, includesid=True)
        #create_survey('', 'tiru/tamB', ['3','2','2','4','5','*2','*2','5','3','recbrands','2','2','*3dep12'], '7961555023', callback=True, inbound=True, includesid=True)
        create_survey('la', 'por', ['*2','4','2','3','3','2','2','2','4','3','2','2','*2'], '7961555007', callback=True, inbound=True, includeid=True, countrycode='0055')
main()