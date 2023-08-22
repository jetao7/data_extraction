import csv
import re
import sys
import argparse


# open file https://www.w3schools.com/python/python_file_open.asp (file reading also from this source)
f = open("sample_mda_autoreboot_2_20052021.ts.txt", "r")


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
          rows += 1

  return p_dict, a_dict

p_d, a_d = get_data()

# find protocol stats totals
def get_ptotals(p_d):
  p_keys = []
  p_values = []
  # protocols section's values
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
    psec_values = p_values[i]

    # get and save the header
    t_header = psec_values[0]
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
        # insert zeros into totals
        p_totals.insert(j, zeros)

      # for each column within the row...
      for l in range(len(psec_values[j]) - 1):
        # +1 to skip name
        p_totals[j][l+1] += int(psec_values[j][l+1])

      # if not 1st section and name was missing in prev section...
      if(i != 0) and (current_name not in psec_names):
        # add new name to list of occured names
        psec_names.append(current_name)

      zeros = []

  # sort by names: https://stackoverflow.com/questions/21068315/python-sort-by-first-element-of-list
  p_totals.sort(key=lambda x: x[0])
  # insert the header
  p_totals.insert(0, t_header)

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
  a_groups = list(a_keygroups.keys())
  num_groups = len(a_keygroups)
  asec_names = []
  current_name = ""
  zeros = []
  # application stats totals
  a_totals = []
  # get group's number(1:1, etc.)
  g_num = ""
  # list of group numbers
  g_nums = []

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
          a_totals.insert(q, zeros)
        
        # for every piece of data within the row...
        for r in range(len(a_groupvalues[q]) - 1):
          # +1 to skip header and names
          a_totals[q][r+1] += int(a_groupvalues[q][r+1])
        
        # if not 1st key and name was missing...
        if(n != 0) and (current_name not in asec_names):
          # add new name to previous list of names
          asec_names.append(current_name)

        zeros = []

    g_num = re.search("[0-9]:[0-9]", a_groups[m])
    # add found group number to list
    g_nums.append(g_num.group())

    # sort by names: https://stackoverflow.com/questions/21068315/python-sort-by-first-element-of-list
    a_totals.sort(key=lambda y: y[0])
    # add header to totals
    a_totals.insert(0, t_header)

    ta_dict.update({a_groupkey:a_totals})
    a_totals = []


  return ta_dict, a_groups, g_nums

a_t, a_g, group_nums = get_atotals(a_d)


# get top <n> protocal stats
def get_ptop(p_t, top_num, column):
  # top n protocols
  ptop = {}
  #current row's total
  row_total = 0
  # each row's values
  row_values = []
  # each row's names
  row_names = []
  # smallest num from top 10
  s_num = 0
  # all other protocols totals together
  p_rest = 0
  # the given column's header position
  c_num = 0

  # take first <n> row of values
  for s in range(1, top_num + 1):
    # if no column specified...
    if(column == "sba + nba"):
      # add sba and nba of each row
      row_total = p_t[s][1] + p_t[s][7]
    else:
      # get column's index from header
      c_num = p_t[0].index(column)
      row_total = p_t[s][c_num]
    row_name = p_t[s][0]
    # add to values and names lists
    row_values.append(row_total)
    row_names.append(row_name)

  # for each of the remaining rows...
  for t in range(top_num + 2, len(p_t)):
    # if no column specified...
    if(column == "sba + nba"):
      row_total = p_t[t][1] + p_t[t][7]
    else:
      # get column's index from header
      c_num = p_t[0].index(column)
      row_total = p_t[t][c_num]
    row_name = p_t[t][0]
    # get smallest num from top10
    s_num = min(row_values)
    if(row_total > s_num):
      # take index of smallest num 
      # replace it with the row name and total
      row_names[row_values.index(s_num)] = row_name
      row_values[row_values.index(s_num)] = row_total
      # add replaced smallest num to rest
      p_rest += s_num
    else:
      p_rest += (row_total)
  
  # update dict with names paired with their values
  for u in range(len(row_names)):
    ptop.update({row_names[u]:row_values[u]})

  # sort by greatest to least: https://www.freecodecamp.org/news/sort-dictionary-by-value-in-python/
  ptop = sorted(ptop.items(), key=lambda x:x[1], reverse=True)

  # add rest of protocols to totals
  ptop.append(("rest", p_rest))

  return ptop


# get top <n> applications
def get_atop(a_t, top_num, column):
  # top <n>
  atop = {}
  # current group's top
  gtop = {}
  # get list of app groups
  at_groups = list(a_t.keys())
  # get list of group values
  at_values = list(a_t.values())
  # each individual groups' values
  g_values = []
  #current row's total
  row_total = 0
  # each row's values
  row_values = []
  # each row's names
  row_names = []
  # smallest num from top 10
  s_num = 0
  # all other protocols totals together
  a_rest = 0

  # for every group...
  for i in range(len(at_groups)):
    # get current groups' values
    g_values = at_values[i]

    # if group doesn't have <n> applications...(+1 to skip header)
    if(len(g_values) <= top_num + 1):
      # for every application...
      for j in range(1, len(g_values)):
        # if no column specified...
        if(column == "sba + nba"):
          # add sba and nba of each row
          row_total = g_values[j][1] + g_values[j][7]
        else:
          # get column's index from header
          c_num = g_values[0].index(column)
          row_total = g_values[j][c_num]
        row_name = g_values[j][0]
        # add to values and names lists
        row_values.append(row_total)
        row_names.append(row_name)
    else:
      # take first 10 row of values
      for s in range(1, top_num + 1):
        # if no column specified...
        if(column == "sba + nba"):
          # add sba and nba of each row
          row_total = g_values[s][1] + g_values[s][7]
        else:
          # get column's index from header
          c_num = g_values[0].index(column)
          row_total = g_values[s][c_num]
        row_name = g_values[s][0]
        # add to values and names lists
        row_values.append(row_total)
        row_names.append(row_name)

      # for each of the remaining rows...
      for t in range(12, len(g_values)):
        # if no column specified...
        if(column == "sba + nba"):
          # add sba and nba of each row
          row_total = g_values[t][1] + g_values[t][7]
        else:
          # get column's index from header
          c_num = g_values[0].index(column)
          row_total = g_values[t][c_num]
        row_name = g_values[t][0]
        # get smallest num from top10
        s_num = min(row_values)
        if(row_total > s_num):
          # take index of smallest num 
          # replace it with the row name and total
          row_names[row_values.index(s_num)] = row_name
          row_values[row_values.index(s_num)] = row_total
          a_rest += s_num
        else:
          a_rest += row_total
    
    # update dict with names paired with their values
    for u in range(len(row_names)):
      gtop.update({row_names[u]:row_values[u]})

    # sort by greatest to least: https://www.freecodecamp.org/news/sort-dictionary-by-value-in-python/
    gtop = sorted(gtop.items(), key=lambda x:x[1], reverse=True)

    # add rest of applications to totals
    gtop.append(("rest", a_rest))

    atop.update({at_groups[i]:gtop})

    gtop = {}
    row_names = []
    row_values = []
    a_rest = 0

  return atop


# get top 10 protocol percents
def get_ppercent(p_top):
  # protocol percents
  pp_list = []
  # each value's percent
  percent = 0.0
  # sum of top 10's values
  sum = 0
  
  # get sum
  for u in range(len(p_top)):
    sum += p_top[u][1]
  
  # get percents
  for v in range(len(p_top)):
    percent = round(p_top[v][1]/sum*100, 4)
    pp_list.append(percent)
  
  return pp_list


# get top 10 application percents
def get_apercent(a_top):
  # application percents
  a_p = {}
  # list of app groups
  a_groups = list(a_top.keys())
  # list of app group values
  a_values = list(a_top.values())
  # individual group's values
  g_values = []
  # each value's percent
  percent = 0.0
  # list of group's percents
  g_p = []
  # sum of top 10's values
  sum = 0
  
  # for every group...
  for i in range(len(a_groups)):
    # current group's values
    g_values = a_values[i]

    # get sum
    for u in range(len(g_values)):
      sum += g_values[u][1]
    
    # get percents
    for v in range(len(g_values)):
      percent = round(g_values[v][1]/sum*100, 4)
      g_p.append(percent)

    # add percents to dict
    a_p.update({a_groups[i]:g_p})
    g_p = []
    sum = 0

  return a_p


# get the top10 protocol chart
def get_pchart(top_pp, p_top):
  # bar chart
  chart = ""
  chart_name = ""
  # num stars to show in bar
  num_stars = 0
  # current percent
  percent = ""
  # add stars to each bar
  count = 0
  
  # for every percent
  for w in range(len(top_pp)):
    # increment by scale of 5
    for x in range(0, 101, 5):
      # if the % is < x...
      if(top_pp[w] < x):
        num_stars = count
        break
      # add a star every increment of 5
      count += 1
    chart_name = p_top[w][0]
    # add a bar to the chart
    chart = "*" * num_stars
    percent = str(top_pp[w]) + "%"
    # format chart to be vertically aligned: https://www.geeksforgeeks.org/string-alignment-in-python-f-string/
    # print each row of the chart
    print(f"{chart_name : <20}{chart : >15}{percent : >20}")
    count = 0


# get the top10 application chart
def get_achart(top_ap, a_top, group_nums):
  # bar chart
  chart = ""
  chart_name = ""
  # app groups
  a_groups = list(top_ap.keys())
  # app percents
  a_percents = list(top_ap.values())
  # each group's percents
  g_percents = []
  # app values(names and values)
  a_values = list(a_top.values())
  # each group's values(names and values)
  g_values = []
  # num stars to show in bar
  num_stars = 0
  # current percent
  percent = ""
  # add stars to each bar
  count = 0

  # for every group...
  for i in range(len(a_groups)):
    g_percents = a_percents[i]
    g_values = a_values[i]
    # output group on chart
    print("GROUP", group_nums[i])
    # for every percent
    for w in range(len(g_percents)):
      # increment by scale of 5
      for x in range(0, 101, 5):
        # if the % is < x...
        if(g_percents[w] < x):
          num_stars = count
          break
        # add a star every increment of 5
        count += 1
      chart_name = g_values[w][0]
      # add a bar to the chart
      chart = "*" * num_stars
      percent = str(g_percents[w]) + "%"
      # format chart to be vertically aligned: https://www.geeksforgeeks.org/string-alignment-in-python-f-string/
      # print each row of the chart
      print(f"{chart_name : <30}{chart : >20}{percent : >20}")
      count = 0
    print("")


#command line input using argparse
#https://www.geeksforgeeks.org/command-line-arguments-in-python/ and 
#https://www.tutorialspoint.com/python/python_command_line_arguments.htm
#https://realpython.com/command-line-interfaces-python-argparse/#customizing-your-command-line-argument-parser

#help screen
des = "Get summarized data of Protocol and Application Statistics"

parser = argparse.ArgumentParser(prog = "ProtoAppWizard", description = des, epilog = "Thanks for using %(prog)s! >:)")
# add option without argument: https://stackoverflow.com/questions/5262702/argparse-module-how-to-add-option-without-any-argument
# adding optional arguments
parser.add_argument("-p", "--proto", help = "show summarized Protocol data", action = "store_true")
parser.add_argument("-a <group>", "--app", nargs = "?", help = "show summarized Application data by group or total", action = "append")
parser.add_argument("-top <n> <column> [p or a]", "--top", nargs = "+", help = "show top <num> (default = 10) <column> (default = sba + nba) [Applications or Protocols]", action = "append")
# read arguments from commmand line
args = parser.parse_args()

# 2nd index num based on num args
index_num = 0
# chosen top num
top_num = 0
# chosen column to sort by
column = ""
# list of all app groups' values
a_tvalues = list(a_t.values())
# list of protocol data types, 1: to skip "name"
pdata_types = p_t[0][1:]
# list of app data types 
adata_types = a_tvalues[0][0]
# chosen data type
data_type = ""
# check if given top num is valid
check_num = True
# check if there's an error in args order
order_error = False

# csv file writing
# open new file to write https://python-adv-web-apps.readthedocs.io/en/latest/csv.html#:~:text=files%20with%20Python.-,The%20csv%20module%20in%20Python,any%20script%20that%20uses%20it.&text=Note%20that%20using%20methods%20from,Reading%20and%20Writing%20Files%20here.
csvfile = open('proto_app_stats.csv', 'w', newline='', encoding='utf-8')
c = csv.writer(csvfile)

# if any arguments are passed in
if any(vars(args).values()):
  if(args.proto):
    print("PROTOCOL TOTALS")
    print(p_t)

    c.writerow(["Name", "Protocol Totals"])
    for i in range(1, len(p_t)):
      c.writerow(p_t[i])
    c.writerow("")

  elif(args.app):
    # if a group is given...
    if(args.app[0] in group_nums):
      for i in range(len(group_nums)):
        if(args.app[0] == group_nums[i]):
          print("GROUP", group_nums[i])
          # print and get the applicaition totals of the specified key/group
          print(a_t.get(a_g[i]))
          for j in range(len(a_t.get(a_g[i]))):
            c.writerow(a_t.get(a_g[i])[j])
    else:
      print("APPLICATION TOTALS")
      print(a_t)  

    # for every group...
    for k in range(len(a_t.keys())):
      c.writerow(["Name", "App totals from " + list(a_t.keys())[k]])
      # for every groups' values...
      for l in range(1, len(a_tvalues[k])):
        c.writerow(a_tvalues[k][l])
      c.writerow("")

  elif(args.top):
    # if p or a is last...
    if((args.top[0][-1] == "p") or (args.top[0][-1] == "a")):
      # if only p or a is passed in...
      if(len(args.top[0]) == 1):
        top_num = 10
        column = "sba + nba"
        data_type = "sba"
        check_num = False

      # if only p or a and top num/column are passed in...
      elif(len(args.top[0]) == 2):
        # see if arg is an int
        try:
          int(args.top[0][0])
        # if not, must be a column
        except:
          column = args.top[0][0]
          data_type = column
          top_num = 10
          # don't check if top num valid
          check_num = False
        # otherwise, it's a selected top num, no column
        else:
          column = "sba + nba"
          data_type = "sba"

      # if everything is passed in...
      else:
        # see if arg is an int
        try:
          int(args.top[0][0])
        # if not, print order error
        except:
          print("arg error: please enter in the following format: -top <n> <column> [p or a]")
          order_error = True
        else:
          column = args.top[0][1]
          data_type = column

      if(order_error == False):
        if(check_num == True):
          # if the top given num is higher than the num of protocols...
          if((int(args.top[0][0]) > len(p_t) + 1) or (int(args.top[0][0]) < 1)):
            # set to default
            top_num = 10
          else:
            # get the wanted top num
            top_num = int(args.top[0][0])
        check_num = True

        # check if last arg is a p or a  
        if(args.top[0][-1] == "p"):
          if(data_type not in pdata_types):
            print("valid error: column not in stats")
          else:
            print("TOP", top_num, "PROTOCOL TOTALS (" + column + ")")
            p_top = get_ptop(p_t, top_num, column)
            print(p_top)
            print("")
            print("PERCENTS")
            top_pp = get_ppercent(p_top)
            print(top_pp)
            print("")
            print("CHART")
            get_pchart(top_pp, p_top)

            c.writerow(["Name", "Top " + str(top_num) + " Protocol Totals (" + column + ")"])
            for m in range(len(p_top)):
              c.writerow(p_top[m])

        elif(args.top[0][-1] == "a"):
          if(data_type not in adata_types):
            print("valid error: column not in stats")
          else:
            print("TOP", top_num, "APPLICATION GROUP TOTALS (" + column + ")")
            a_top = get_atop(a_t, top_num, column)
            print(a_top)
            print("")
            print("PERCENTS")
            top_ap = get_apercent(a_top)
            print(top_ap)
            print("")
            print("CHART(S)")
            get_achart(top_ap, a_top, group_nums)
            
            a_topvalues = list(a_top.values())
            # for every group...
            for n in range(len(a_top.keys())):
              c.writerow(["Name", "Top " + str(top_num) + " Application Totals (" + column + ") " + list(a_top.keys())[n]])
              # for every groups' values...
              for o in range(len(a_topvalues[n])):
                # write each pair of values
                c.writerow(a_topvalues[n][o])
              c.writerow("")

      order_error = False

    # if p or a is not in last position...
    else:
      if(len(args.top[0]) == 1):
        print("valid error: please enter p or a")
      else:
        print("arg error: please enter in the following format: -top <n> <column> [p or a]")

else:
  # print the help menu again
  parser.print_help()


#C:\Users\jetao\AppData\Local\Programs\Python\Python311\python.exe
