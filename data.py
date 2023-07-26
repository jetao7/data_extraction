import csv
import re


# open file https://www.w3schools.com/python/python_file_open.asp (file reading also from this source)
# f = open("sample_mda_autoreboot_2_20052021.ts.txt", "r")
f = open("comcast_multiple_esavms.txt", "r")
# open new file to write https://python-adv-web-apps.readthedocs.io/en/latest/csv.html#:~:text=files%20with%20Python.-,The%20csv%20module%20in%20Python,any%20script%20that%20uses%20it.&text=Note%20that%20using%20methods%20from,Reading%20and%20Writing%20Files%20here.
csvfile = open('protocol_statistics.csv', 'w', newline='', encoding='utf-8')
c = csv.writer(csvfile)


# collect and store data from file
def get_data():
  done = False
  start = False
  line = ""
  # dictionary storing data section
  p_dict = {}
  # key of dictionary
  d_key = ""
  # section of data
  data_sec = [[]]
  data_line = []
  guard_counter = 1000000000
  rows = 0
     
  # while data not done extracting...
  while(done == False and guard_counter != 0):
    guard_counter -= 1
    # read line from file
    line = f.readline()

    if("tmd:" not in line):
      # # if no esa or snip found in the line, stop data extraction
      if(re.search("esa-[0-9]/[0-9]|[0-9]/[0-9]", line) == None) and ("<snip>" not in line):
        done = True
      # if data extraction hasn't started...
      elif(start == False): 
        # if line contains the string from https://realpython.com/python-string-contains-substring/
        if("Application-Assurance Protocol Statistics" in line):
          data_sec = [[]]
          # skip non-data line
          f.readline()
          line = f.readline()
          # set dictionary key as esa-...
          d_key = re.findall("esa-[0-9]/[0-9]|[0-9]/[0-9]", line)[0]
          # get rid of unwanted characters
          line = line.replace(d_key + ":   ", "")
          line = line.replace("\"", "")
          # remove extra line space https://www.w3schools.com/python/ref_string_rstrip.asp
          line = line.strip()
          # assign the heading, split function from: https://www.w3schools.com/python/ref_string_split.asp
          data_line = line.split(",")
          # insert line of data into data section https://www.javatpoint.com/python-2d-array#:~:text=Insert%20elements%20in%20a%202D,and%20location%20to%20be%20inserted.&text=%23%20Write%20a%20program%20to%20insert,two%20dimensional)%20array%20of%20Python.
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
          data_sec.pop()
          # add data to the dictionary https://www.programiz.com/python-programming/methods/dictionary/update
          p_dict.update({d_key:data_sec})
          # separate data in csv file
          c.writerow("")
          start = False

        # otherwise, keep adding to current data set
        else:
          line = line.replace(d_key + ":   ", "")
          line = line.replace("\"", "")
          line = line.strip()
          data_line = line.split(",")
          # add line of data to array
          data_sec.insert(rows, data_line)
          c.writerow(data_line)
          rows += 1

  return p_dict

p_d = get_data()
print(p_d)


# find totals of each data type
def get_totals(p_d):
  p_dict = p_d
  # dictionary storing totals of data
  t_dict = {}
  p_keys = []
  p_values = []
  sec_values = []
  t_header = []
  totals = []
  zeros = []

  # list of all keys in dictionary
  p_keys = list(p_dict.keys())
  # list of all values in dictionary
  p_values = list(p_dict.values())

  # for every key...
  for i in range(len(p_keys)):
    sec_key = p_keys[i]
    sec_values = p_values[i]

    # get rid of name for header
    sec_values[0].pop(0)
    t_header = sec_values[0]
    totals.insert(0, t_header)
    # get rid of headers from data
    sec_values.pop(0)
    # get rid of names from data
    for j in range(len(sec_values)):
      sec_values[j].pop(0)
   
    # initialize totals with zeros
    for k in range(len(t_header)):
      zeros.append(0)
    totals.insert(1, zeros)
   
    # for each row of values...
    for l in range(len(sec_values)):
      # for each column within the row...
      for m in range(len(sec_values[l])):
        totals[1][m] += int(sec_values[l][m])
   
    t_dict.update({sec_key:totals})
    totals = []
    zeros = []

  return t_dict

t_d = get_totals(p_d)
# print(t_d)




# for j in range(len(total_line)):
#   totals[1][j] += int(total_line[j])
# for i in range(len(total_line)):
#           totals[1].insert(i, 0)




# for j in range(rows):
#   for k in range(columns):
#     print(data[j][k], end="")




   
       


 

