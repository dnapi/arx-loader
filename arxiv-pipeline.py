# this programm download the tex files of arxiv articles given by list.
# list of articles to download is defined by  'list_of_arxs'.
# the files are saved in the directory defined by 'working_dir'
# Only for the articles after March 2007.
# Discription of indentifier could be found at https://arxiv.org/help/arxiv_identifier

# Please, specify in file.py variables 'list_of_arxs' and 'working_dir'
# that define list articles and working directory


import arxiv
import tarfile
import shutil
from os import listdir, remove
from os.path import isfile, join
import datetime
import time

# Making a list of papers we want to download given by the indentifier in the form yymm.xxxxx
# all since Jan 1 20208 can be listed as 
list_of_arxs=[str(y)+(f'{m:02}.') + (f'{n:05}') for y in range(10,23) for m in range(1,13)  for n in range(1,100000)]
#list_of_arxs=['2205.12948','2205.10000','2205.10001']

working_dir ="./mydir"       # specify working directory where tex files will be downloaded
temp_dir='./mydir/temp'  # specify temporary directory 
i_max='0000.99999' # flag used to stop when the index of xxxxx is above the maximal value submitted in the given month 
num_of_requests=0   #counder of requests number
now0 = datetime.datetime.now()   # start time of the program 
now1 = datetime.datetime.now()   # start time of working on certain arxive paper
delay_time_after_connection_error=32  # Helps to tackle the HTTPError

def save_tex_file(i):  # where i is arxiv's number e.g. i = '1601.00001'
    paper = next(arxiv.Search(id_list=[i]).results())
    paper.download_source(dirpath=working_dir, filename= i + ".tar.gz")
    tar = tarfile.open(working_dir +'/'+ i + ".tar.gz")
    tar.extractall(temp_dir)
    tar.close()
    only_tex_files = [f for f in listdir(temp_dir) if isfile(join(temp_dir, f)) and f.endswith(".tex")]
    if len(only_tex_files)>0:
        shutil.copyfile(temp_dir+'/'+only_tex_files[0], working_dir + '/' + i +'.tex')
        print('arxiv', i, ' is downloaded.')
    else:
        print('no .tex file in ',listdir(temp_dir))
        open(working_dir + '/' + i +'.notex','a').close()
    remove(working_dir+'/' + i + ".tar.gz")
    #os.rmdir()
    shutil.rmtree(temp_dir)
    #list_of_categories.append([i, paper.categories])

# here we check that is was not already downloaded and that this arxive exist
def test_to_download(num):
    test_tex=list_of_arxs[num]+'.tex' not in listdir(working_dir)
    test_notex=list_of_arxs[num]+ '.notex' not in listdir(working_dir)
    test_end_of_arxiv_num=list_of_arxs[num][0:5] != i_max[0:5]
    result = test_tex and test_notex and test_end_of_arxiv_num
    return result

gen = (num for num in range(len(list_of_arxs)) if test_to_download(num))

for num in gen:
    i=list_of_arxs[num]
#    if i + '.tex' not in listdir("./mydir2") and i + '.notex' not in listdir("./mydir2") and i[0:5] != i_max[0:5]
    print('Starting ', i, ';   Num of request=', num_of_requests+1)
    num_of_requests+=1
    try:
        save_tex_file(i)
        i_max='0000.99999'
        now2 = datetime.datetime.now()
        delay_time= 3.1 - (now2-now1).seconds
        if delay_time > 0:   
            print('time delay=',delay_time,'\n')
            time.sleep(delay_time)    # Helps to avoid ConnectionResetError(104, 'Connection reset by peer')
        else:
            print('\n')
        if delay_time_after_connection_error>60: # Helps to tackle  ConnectionResetError(104, 'Connection reset by peer')
            delay_time_after_connection_error = 1
        now1 = datetime.datetime.now()
    except StopIteration:
        i_max=i
        print(i,' no such arxiv')
    except ConnectionResetError:         #ConnectionResetError(104, 'Connection reset by peer')
        now3 = datetime.datetime.now()
        running_time=(now3-now0).seconds
        print('running_time=',running_time, 'sec')
        print('num_of_requests=',num_of_requests)
        print('ConnectionResetError!!!')
        print('delay_time_after_connection_error=',delay_time_after_connection_error)
        time.sleep(delay_time_after_connection_error)
        delay_time_after_connection_error=delay_time_after_connection_error*2
    except Exception as e:  #except HTTPError:
        print(i,'Error: ',e)
        open(working_dir + '/' + i +'.notex','a').close()