import sys
import re
import os
import json

def create_continents_dictionary():
  conts = {"Africa" : ["Burundi", "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Cameroon", "Cape Verde", "Chad", "Comoros", "Republic of the Congo", "Democratic Republic of the Congo", "Cote dIvoire", "Central African Republic", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"], "Asia" : ["Northern Mariana Islands", "Guam", "French Polynesia", "Macau", "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "Peoples Republic of China", "Republic of China Taiwan", "Hong Kong", "East Timor", "India", "Indonesia", "Iran", "Iraq", "Israel", "Palestine", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Philippines", "Qatar", "Russia", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", "Tajikistan", "Thailand", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"], "Europe" : ["Gibraltar", "Reunion", "Mayotte", "Kosovo", "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"], "North America" : ["Cayman Islands", "French West Indies", "Aruba", "Turks and Caicos Islands", "Anguilla", "Bermuda", "British Virgin Islands", "United States Virgin Islands", "Canada", "Mexico", "Montserrat", "Curacao", "United States"], "Central America and the Antilles" : ["Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Nicaragua", "Panama", "Puerto Rico", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago", "Turks and Caicos Islands"], "South America" : ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"], "Oceania" : ["New Caledonia", "Norfolk Island", "Cook Islands", "Australia", "New Zealand", "Fiji", "Papua New Guinea", "Solomon Islands", "Vanuatu", "Kiribati", "Marshall Islands", "Micronesia", "Niue", "Nauru", "Palau", "American Samoa", "Samoa", "Tonga", "Tuvalu"]}
  lookup_conts = {}
  for cont in conts:
    for country in conts[cont]:
      lookup_conts[country] = cont
  return lookup_conts

def parse_lines_into_links(filename, cont_dict):
  '''out_United_States'''
  source_name = " ".join(re.sub(r'out_','',filename).split("_"))[12:]
  source = {"name": source_name, "continent": cont_dict[source_name]}
  d = {}
  link_types = {"free":[], "required": [], "onarrival": [], "refused": []}
  for i,line in enumerate(open(filename).readlines()):
    line = line.rstrip()
    if (i%3==0):
      target_name = line.replace("'", "").replace("&#039;", "").replace("(Taiwan)", "Taiwan").replace("\xc3\xa7", "c")
      target = {"name": target_name, "continent": cont_dict[target_name]}
    elif (i%3==1):
      status = line.split(":")[0].split("-")[1]
      term = line.split(":")[1].rstrip() if len(line.split(":"))>1 else ""
    else:
      notes = line.split(":")[1] if len(line.split(":"))>1 else ""
      link_types[status].append({"source": source, "target": target, "term": term, "notes": notes})
  return link_types

def main(data_folder):
  nodes = []
  countries = create_continents_dictionary()
  for x in countries:
    nodes.append({"name": x, "continent": countries[x]})
  files = os.listdir(data_folder)
  links = {"free":[], "required": [], "onarrival": [], "refused": []}
  for f in files:
    out = parse_lines_into_links("output_data/" + f, countries)
    for s in links:
      links[s] += out[s]
  return json.dumps({"nodes": nodes, "links": links["refused"]}) 

if __name__=="__main__":
  print main("output_data")
