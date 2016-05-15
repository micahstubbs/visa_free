import sys, re, os, json

CONTS = {"Africa" : ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros", "Cote dIvoire", "Democratic Republic of the Congo", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Republic of the Congo", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"], "Asia" : ["Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "East Timor", "French Polynesia", "Guam", "Hong Kong", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Macau", "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", "Northern Mariana Islands", "Oman", "Pakistan", "Palestine", "Peoples Republic of China", "Philippines", "Qatar", "Republic of China Taiwan", "Russia", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", "Tajikistan", "Thailand", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"], "Europe" : ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", "Gibraltar", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta", "Mayotte", "Moldova", "Monaco", "Montenegro", "Netherlands", "Norway", "Poland", "Portugal", "Reunion", "Romania", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"], "North America" : ["Anguilla", "Aruba", "Bermuda", "British Virgin Islands", "Canada", "Cayman Islands", "Curacao", "French West Indies", "Mexico", "Montserrat", "United States Virgin Islands", "United States"], "Central America and the Antilles" : ["Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Nicaragua", "Panama", "Puerto Rico", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago", "Turks and Caicos Islands"], "South America" : ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"], "Oceania" : ["American Samoa", "Australia", "Cook Islands", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Caledonia", "New Zealand", "Niue", "Norfolk Island", "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu" ]}

def create_continents_dictionary():
  lookup_conts = {}
  for cont in CONTS:
    for i,country in enumerate(CONTS[cont]):
      country_rank = (float(i+1))/len(CONTS[cont])
      lookup_conts[country] = (cont, country_rank)
  return lookup_conts

def parse_lines_into_links(filename, cont_dict):
  '''out_United_States'''
  d = {}
  source_name = " ".join(re.sub(r'out_','',filename).split("_"))[12:]
  source = {"name": source_name, "continent": cont_dict[source_name][0], 'y': cont_dict[source_name][1]}
  link_types = {"free":[], "required": [], "onarrival": [], "refused": []}
  for i,line in enumerate(open(filename).readlines()):
    line = line.rstrip()
    if (i%3==0):
      target_name = line.replace("'", "").replace("&#039;", "").replace("(Taiwan)", "Taiwan").replace("\xc3\xa7", "c")
      target = {"name": target_name, "continent": cont_dict[target_name][0], 'y': cont_dict[target_name][1]}
    elif (i%3==1):
      status = line.split(":")[0].split("-")[1]
      term = line.split(":")[1].rstrip() if len(line.split(":"))>1 else ""
    else:
      notes = line.split(":")[1] if len(line.split(":"))>1 else ""
      link_types[status].append({"source": source, "target": target, "term": term, "notes": notes})
  return link_types

def compute_visa_isomorphism_classes(links):
  country_sets, isomorphic_countries,  isom_classes = {}, {}, {}
  for y in CONTS:
    country_sets[y] = {}
    for c in CONTS[y]:
      country_sets[y][c] = {"free": set(), "required": set(), "onarrival": set(), "refused": set()}
  for l in links:
    for n in links[l]:
      s = n["source"]
      country_sets[s["continent"]][s["name"]][l].add(n["target"]["name"])
  for t in ["free", "onarrival", "required", "refused"]:
    for x in country_sets:
      for y in country_sets[x]:
        if y in isomorphic_countries:
          isomorphic_countries[y].update({t: []}) 
        else: 
          isomorphic_countries[y] = {t: []}
        for z in country_sets[x]:
          if country_sets[x][y][t] == country_sets[x][z][t]:
            isomorphic_countries[y][t].append(z)
    isom_classes[t] = [(x,isomorphic_countries[x][t]) for x in [c for c in isomorphic_countries if len(isomorphic_countries[c][t])>1]]
  return isom_classes

def create_pairwise_networks(nodes, links):
  pairwise_nodes, pairwise_nodes_old, pairwise_links = {}, {}, {}
  for a in CONTS:
    for b in CONTS:
      pairwise_nodes[a + "-" + b] = []
      for d in CONTS[a]:
        pairwise_nodes[a + "-" + b].append({"name": d, "continent": a, "type": "origin", "y": nodes[d][1]})
      for c in CONTS[b]:
        for t in ["free", "onarrival", "required", "refused"]:
          pairwise_nodes[a + "-" + b].append({"name": c , "continent": b, "type": t, "y": nodes[c][1]})
      pairwise_links[a + "-" + b] = []
      for t in links:
        for l in links[t]:
          if (l["source"]["continent"] == a and l["target"]["continent"] == b): 
            source_node = {"name": l["source"]["name"], "continent": l["source"]["continent"] , "type": "origin", "y": l["source"]["y"]}
            target_node = {"name": l["target"]["name"], "continent": l["target"]["continent"] , "type": t, "y": l["target"]["y"]}
            pairwise_links[a + "-" + b].append({"source": source_node, "target": target_node, "term": l["term"] , "notes": l["notes"]})
      pairwise_nodes[a + "-" + b] = []
      for d in CONTS[a]:
        pairwise_nodes[a + "-" + b].append({"name": d, "continent": a, "type": "origin", "y": nodes[d][1]})
      for l in pairwise_links[a + "-" + b]:
        if l["target"] not in pairwise_nodes[a + "-" + b]:
          pairwise_nodes[a + "-" + b].append(l["target"])
  return (pairwise_nodes, pairwise_links)


def compute_y_values(nodes, links):
  type_lists = {}
  for a in CONTS:
    for b in CONTS:
      type_lists[a + "-" + b] = {}
      for t in ["required", "refused", "onarrival", "free"]:
        type_lists[a + "-" + b][t] = filter(lambda l: l["type"] == t, nodes[a + "-" + b])
        order = len(type_lists[a + "-" + b][t])
        indices = {}
        for i,x in enumerate([z["name"] for z in type_lists[a + "-" + b][t]]):
          indices[x] = i 
        map(lambda m: m.update({"y": float(indices[m["name"]]+1)/order }), filter(lambda l: l["type"] == t, nodes[a + "-" + b]))
        map(lambda s: s["target"].update({"y": float(indices[s["target"]["name"]]+1)/order}), filter(lambda l: l["target"]["type"] == t, links[a + "-" + b]))
  return nodes, links


def main(data_folder, output_key=""):
  nodes = []
  countries = create_continents_dictionary()
  for x in countries:
    nodes.append({"name": x, "continent": countries[x][0], "y": countries[x][1]})
  files = os.listdir(data_folder)
  links = {"free":[], "required": [], "onarrival": [], "refused": []}
  for f in files:
    out = parse_lines_into_links("output_data/" + f, countries)
    for s in links:
      links[s] += out[s]
  pair_dicts = create_pairwise_networks(countries, links)
  print pair_dicts[0]["Asia-North America"]
  #return json.dumps({"pairwise_nodes": pair_dicts[0], "pairwise_links": pair_dicts[1]})
  #return json.dumps({"nodes": nodes, "links": links[output_key]}) 
  u, v = compute_y_values(pair_dicts[0], pair_dicts[1])
  return json.dumps({"pairwise_nodes": u, "pairwise_links": v})

'''CL arguments are data_folder and output_key'''
if __name__=="__main__":
  print main(sys.argv[1], sys.argv[2])