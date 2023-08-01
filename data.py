import csv
import re
import copy


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
  guard_counter = 1291
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


# find totals of each data type
def get_totals(p_d, a_d):
  # dictionary storing protocol totals
  tp_dict = {}
  p_keys = []
  p_values = []
  # protocols section's keys and values
  psec_key = ""
  psec_values = []
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

    # get rid of name for header
    psec_values[0].pop(0)
    t_header = psec_values[0]
    p_totals.insert(0, t_header)
    # get rid of headers from data
    psec_values.pop(0)
    # get rid of names from data
    for j in range(len(psec_values)):
      psec_values[j].pop(0)
   
    # initialize totals with zeros
    for k in range(len(t_header)):
      zeros.append(0)
    p_totals.insert(1, zeros)
   
    # for each row of values...
    for l in range(len(psec_values)):
      # for each column within the row...
      for m in range(len(psec_values[l])):
        p_totals[1][m] += int(psec_values[l][m])
   
    tp_dict.update({psec_key:p_totals})
    p_totals = []
    zeros = []


  # dictionary storing application totals
  ta_dict = {}
  # list of each keys' groups with their data sections
  a_keys = list(a_d.values())
  a_keygroups = a_keys[0]
  num_groups = len(a_keygroups)
  a_totals = []
  # print(a_keygroups)

  #application stats totals
  # for number of groups...
  for m in range(num_groups):
    # for every key...
    for n in range(len(a_keys)):
      # get each individual keys' groups
      a_keygroups = a_keys[n]
      # print(a_keygroups)
      # # for every group in each key...
      # for n in range(len(a_keygroups)):
      # get group
      a_groupkey = list(a_keygroups.keys())[m]
      # get each groups' values
      a_groupvalues = list(a_keygroups.values())[m]
      # get rid of name for header
      a_groupvalues[0].pop(0)
      t_header = a_groupvalues[0]
      if(n == 0):
        # add header to totals
        a_totals.insert(0, t_header)
        # initialize totals with zeros
        for o in range(len(t_header)):
          zeros.append(0)
        a_totals.insert(1, zeros)
      # get rid of headers
      a_groupvalues.pop(0)
      # get rid of names from data
      for p in range(len(a_groupvalues)):
        a_groupvalues[p].pop(0)

      # for every row of data...
      for q in range(len(a_groupvalues)):
        # for every piece of data within the row...
        for r in range(len(a_groupvalues[q])):
          a_totals[1][r] += int(a_groupvalues[q][r])

    ta_dict.update({a_groupkey:a_totals})
    # print(ta_dict)
    a_totals = []
    zeros = []


  print(ta_dict)
  return tp_dict

tp_d = get_totals(p_d, a_d)
# print(tp_d)
# print(tp_d)
#user input
# exit = False

# while(exit == False):
#   print("What would you like to do?")
#   print("1. Get data")
#   print("2. Get totals from data")
#   print("3. Exit")
#   command = input("Your choice: ")

#   while((command != "1") and (command != "2") and (command != "3")):
#     command = input("Your choice: ")

#   if(command == "1"):
#     print(p_d)
#     print()
#   elif(command == "2"):
#     print(t_d)
#     print()
#   else:
#     exit = True


# for j in range(len(total_line)):
#   totals[1][j] += int(total_line[j])
# for i in range(len(total_line)):
#           totals[1].insert(i, 0)




# for j in range(rows):
#   for k in range(columns):
#     print(data[j][k], end="")




   
       


 

