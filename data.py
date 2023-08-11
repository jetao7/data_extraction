import csv
import re
import sys
import argparse


# open file https://www.w3schools.com/python/python_file_open.asp (file reading also from this source)
f = open("sample_mda_autoreboot_2_20052021.ts.txt", "r")
# f = open("comcast_multiple_esavms.txt", "r")
# open new file to write https://python-adv-web-apps.readthedocs.io/en/latest/csv.html#:~:text=files%20with%20Python.-,The%20csv%20module%20in%20Python,any%20script%20that%20uses%20it.&text=Note%20that%20using%20methods%20from,Reading%20and%20Writing%20Files%20here.
csvfile = open('protocol_statistics.csv', 'w', newline='', encoding='utf-8')
c = csv.writer(csvfile)


# collect and store data from file
def get_data():
  done = False
  start = False
  line = ""
  # dictionary storing protocol stats
  p_dict = {}
  # dictionary storing application stats
  a_dict = {}
  # dictionary storing all groups
  g_dict = {}
  group = ""
  # original section key (for if there's only one key in file)
  o_key = ""
  # most recent line's key
  new_key = ""
  # if looking for application stats
  a_stats = False
  # if looking for a new key
  find_new_key = False
  # section of data
  data_sec = [[]]
  data_line = []
  guard_counter = 1111
  rows = 0
     
  # while data not done extracting...
  while(done == False and guard_counter != 0):
    guard_counter -= 1
    # read line from file
    line = f.readline()

    if("tmd:" not in line):
      # # if no esa or snip found in the line, stop data extraction
      if(re.search("esa-[0-9]/[0-9]|[0-9]/[0-9]", line) == None) and ("<snip>" not in line) or (guard_counter == 0):
        # when done extracting, update dictionary with original section's key
        a_dict.update({o_key:g_dict})
        done = True
      # if data extraction hasn't started...
      elif(start == False): 
        # if line contains the string from https://realpython.com/python-string-contains-substring/
        if("Application-Assurance Protocol Statistics" in line) or ("Application-Assurance Application Statistics" in line):
          if("Application-Assurance Application Statistics" in line):
            # get application group
            group = re.findall("group [0-9]:[0-9]", line)[0]
            a_stats = True
          else:
            a_stats = False
          data_sec = [[]]
          # skip non-data line
          f.readline()
          line = f.readline()

          # if finding new key...
          if(find_new_key == True):
            new_key = re.findall("esa-[0-9]/[0-9]|[0-9]/[0-9]", line)[0]
            line = line.replace(new_key + ":   ", "")
          else:
            # set dictionary key as esa-...
            o_key = re.findall("esa-[0-9]/[0-9]|[0-9]/[0-9]", line)[0]
            line = line.replace(o_key + ":   ", "")
          # get rid of unwanted characters
          line = line.replace("\"", "")
          # remove extra line space https://www.w3schools.com/python/ref_string_rstrip.asp
          line = line.strip()
          # assign the heading, split function from: https://www.w3schools.com/python/ref_string_split.asp
          data_line = line.split(",")
          # insert heading into data section https://www.javatpoint.com/python-2d-array#:~:text=Insert%20elements%20in%20a%202D,and%20location%20to%20be%20inserted.&text=%23%20Write%20a%20program%20to%20insert,two%20dimensional)%20array%20of%20Python.
          data_sec.insert(0, data_line)
          # get rid of extra item in list
          data_sec.pop()
          # write on the CSV file
          c.writerow(data_line)
          rows += 1
          start = True

        # if data extraction started...
      else:
        if("===============================================================================" in line):
          # add data to the dictionaries https://www.programiz.com/python-programming/methods/dictionary/update
          # if looking for application stats...
          if(a_stats == True):
            if(new_key != o_key):
              a_dict.update({o_key:g_dict})
              g_dict = {}
              o_key = new_key
            g_dict.update({group:data_sec})
          # if looking for protocol stats...
          else:
            if(find_new_key == True):
              p_dict.update({new_key:data_sec})
            # if no new key found, update by original key
            else:
              p_dict.update({o_key:data_sec})
          # separate data in csv file
          c.writerow("")
          find_new_key = True
          start = False

        # otherwise, keep adding to current data set
        else:
          if(find_new_key == True):
            line = line.replace(new_key + ":   ", "")
          else:
            line = line.replace(o_key + ":   ", "")
          line = line.replace("\"", "")
          line = line.strip()
          data_line = line.split(",")
          # add line of data to array
          data_sec.insert(rows, data_line)
          c.writerow(data_line)
          rows += 1

  return p_dict, a_dict

p_d, a_d = get_data()
# print(p_d)
# print(a_d)

# find protocol stats totals
def get_ptotals(p_d):
  # dictionary storing protocol totals
  tp_dict = {}
  p_keys = []
  p_values = []
  # protocols section's keys and values
  psec_key = ""
  psec_values = []
  psec_names = []
  current_name = ""
  t_header = []
  p_totals = []
  zeros = []

  # list of protocol keys
  p_keys = list(p_d.keys())
  # list of protocol values
  p_values = list(p_d.values())

  # protocol stats totals  
  # for every key...
  for i in range(len(p_keys)):
    psec_key = p_keys[i]
    psec_values = p_values[i]

    t_header = psec_values[0]
    # if 1st time, add header to totals
    if(i == 0):
      p_totals.insert(0, t_header)
    # get rid of headers from data
    psec_values.pop(0)

    # for each row of values...
    for j in range(len(psec_values)):
      current_name = psec_values[j][0]
      # if 1st key, add protocol names to list
      if(i == 0):
        # store current row's name
        psec_names.append(current_name)

      # if the protocol is not in the list or it's 1st key...
      if(i == 0) or (current_name not in psec_names):
        # initialize totals with zeros
        # -1 for the name
        for k in range(len(t_header) - 1):
          zeros.append(0)
        zeros.insert(0, current_name)
        # +1 to skip header
        p_totals.insert(j+1, zeros)

      # for each column within the row...
      for l in range(len(psec_values[j]) - 1):
        # +1 to skip header and name
        p_totals[j+1][l+1] += int(psec_values[j][l+1])

      # if not 1st section and name was missing in prev section...
      if(i != 0) and (current_name not in psec_names):
        # add new name to list of occured names
        psec_names.append(current_name)

      zeros = []

  return p_totals

p_t = get_ptotals(p_d)


# find application stats totals
def get_atotals(a_d):
  # dictionary storing application totals
  ta_dict = {}
  # list of each keys' groups with their data sections
  a_keys = list(a_d.values())
  # take 1st keys' groups to find num of groups 
  a_keygroups = a_keys[0]
  num_groups = len(a_keygroups)
  asec_names = []
  current_name = ""
  zeros = []
  # application stats totals
  a_totals = []

  # loop thorugh each of the same groups
  for m in range(num_groups):
    # for every key...
    for n in range(len(a_keys)):
      # get current keys' groups
      a_keygroups = a_keys[n]
      # get group
      a_groupkey = list(a_keygroups.keys())[m]
      # get each groups' values
      a_groupvalues = list(a_keygroups.values())[m]

      t_header = a_groupvalues[0]
      if(n == 0):
        # add header to totals
        a_totals.insert(0, t_header)
      # get rid of headers from data
      a_groupvalues.pop(0)

      # for every row of data...
      for q in range(len(a_groupvalues)):
        current_name = a_groupvalues[q][0]
        # if looping through 1st key
        if(n == 0):
          asec_names.append(current_name)

        if(n == 0) or (current_name not in asec_names):
          # initialize totals with zeros
          # -1 for the name
          for o in range(len(t_header) - 1):
            zeros.append(0)
          zeros.insert(0, current_name)
          # +1 to skip the header
          a_totals.insert(q+1, zeros)
        
        # for every piece of data within the row...
        for r in range(len(a_groupvalues[q]) - 1):
          # +1 to skip header and names
          a_totals[q+1][r+1] += int(a_groupvalues[q][r+1])
        
        # if not 1st key and name was missing...
        if(n != 0) and (current_name not in asec_names):
          # add new name to previous list of names
          asec_names.append(current_name)

        zeros = []

    ta_dict.update({a_groupkey:a_totals})
    a_totals = []

  return ta_dict

a_t = get_atotals(a_d)


# get top 10 protocal and application stats
def get_top10(p_t):
  # top 10 protocols
  top10 = []
  # smallest num from top 10
  s_num = 0

  # take first 10 row of values
  for s in range(1, 11):
    # add sba and nba of each row
    row_total = p_t[s][1] + p_t[s][7]
    top10.append(row_total)

  # for each of the remaining rows...
  for t in range(12, len(p_t)):
    row_total = p_t[t][1] + p_t[t][7]
    # get smallest num from top10
    s_num = min(top10)
    if(row_total > s_num):
      # take index of smallest num
      # replace it with the row total
      top10[top10.index(s_num)] = row_total
      
  return top10

t_10 = get_top10(p_t)


def get_percent(t_10):
  # list of percents
  p_list = []
  # each value's percent
  percent = 0.0
  # sum of top 10's values
  sum = 0
  
  # get sum
  for u in range(len(t_10)):
    sum += t_10[u]
  
  for v in range(len(t_10)):
    percent = round(t_10[v]/sum*100, 2)
    p_list.append(percent)
  
  return p_list

t_10_p = get_percent(t_10)

#command line input using argparse
#https://www.geeksforgeeks.org/command-line-arguments-in-python/ and 
#https://www.tutorialspoint.com/python/python_command_line_arguments.htm

#help screen
des = "ProtoAppWizard 1.0.0 Get summarized data from Protocol and Application Statistics"

parser = argparse.ArgumentParser(description = des)
# add option without argument: https://stackoverflow.com/questions/5262702/argparse-module-how-to-add-option-without-any-argument
# adding optional arguments
parser.add_argument("-p", "--proto", help = "show summarized Protocol data", action = "store_true")
parser.add_argument("-a", "--app", help = "show summarized Application data by group or total", action = "store_true")
parser.add_argument("-t10p", "--top10proto",help = "show top 10 ", action = "store_true")
# read arguments from commmand line
args = parser.parse_args()

# if any arguments are passed in
if any(vars(args).values()):
  if(args.proto):
    print("PROTOCOL TOTALS")
    print(p_t)
  elif(args.app):
    print("APPLICATION TOTALS")
    print(a_t)
  elif(args.top10proto):
    print("TOP 10 PROTOCOL TOTALS")
    print(t_10)
    print("Percents:")
    print(t_10_p)
else:
  # print the help menu again
  parser.print_help()


#C:\Users\jetao\AppData\Local\Programs\Python\Python311\python.exe
