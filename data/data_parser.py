import sys, re, os, json
import networkx as nx
import matplotlib.pyplot as plt

CONTS = {"Africa" : ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros", "Cote dIvoire", "Democratic Republic of the Congo", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea", "Guinea Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Republic of the Congo", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"], "Asia" : ["Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "East Timor", "French Polynesia", "Guam", "Hong Kong", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Macau", "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", "Northern Mariana Islands", "Oman", "Pakistan", "Palestine", "Peoples Republic of China", "Philippines", "Qatar", "Republic of China Taiwan", "Russia", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", "Tajikistan", "Thailand", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"], "Europe" : ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", "Gibraltar", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta", "Mayotte", "Moldova", "Monaco", "Montenegro", "Netherlands", "Norway", "Poland", "Portugal", "Reunion", "Romania", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"], "North America" : ["Anguilla", "Aruba", "Bermuda", "British Virgin Islands", "Canada", "Cayman Islands", "Curacao", "French West Indies", "Mexico", "Montserrat", "Turks and Caicos Islands", "United States Virgin Islands", "United States"], "Central America and the Antilles" : ["Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Nicaragua", "Panama", "Puerto Rico", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago", "Turks and Caicos Islands"], "South America" : ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"], "Oceania" : ["American Samoa", "Australia", "Cook Islands", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Caledonia", "New Zealand", "Niue", "Norfolk Island", "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu" ]}

all_countries = []
for z in CONTS:
  all_countries += CONTS[z]

def create_continents_dictionary():
  lookup_conts = {}
  for cont in CONTS:
    for i,country in enumerate(CONTS[cont]):
      country_rank = (float(i+1))/len(CONTS[cont])
      lookup_conts[country] = (cont, country_rank)
  return lookup_conts

def parse_lines_into_links(filename, cont_dict):
  '''out_United_States'''
  source_name = " ".join(re.sub(r'out_','',filename).split("_"))[12:].replace("Guinea-Bissau", "Guinea Bissau")
  source = {"name": source_name, "continent": cont_dict[source_name][0], 'y': cont_dict[source_name][1]}
  d = {}
  link_types = {"free":[], "required": [], "onarrival": [], "refused": []}
  for i,line in enumerate(open(filename).readlines()):
    line = line.rstrip()
    if (i%3==0):
      target_name = line.replace("'", "").replace("&#039;", "").replace("(Taiwan)", "Taiwan").replace("\xc3\xa7", "c").replace("Guinea-Bissau", "Guinea Bissau")
      target = {"name": target_name, "continent": cont_dict[target_name][0], 'y': cont_dict[target_name][1]}
    elif (i%3==1):
      status = line.split(":")[0].split("-")[1]
      term = line.split(":")[1].rstrip() if len(line.split(":"))>1 else ""
    else:
      notes = line.split(":")[1] if len(line.split(":"))>1 else ""
      link_types[status].append({"source": source, "target": target, "term": term, "notes": notes})
  return link_types

def compute_visa_isomorphism_classes(links):
  country_sets = {}
  for y in CONTS:
    country_sets[y] = {}
    for c in CONTS[y]:
      country_sets[y][c] = {"free": set(), "required": set(), "onarrival": set(), "refused": set()}
  for t in links:
    for n in links[t]:
      s = n["source"]
      country_sets[s["continent"]][s["name"]][t].add(n["target"]["name"])
  isomorphic_countries = {}
  for x in country_sets:
    for y in country_sets[x]:
      isomorphic_countries[y] = {"free":[], "required": [], "onarrival": [], "refused": []}
      for z in country_sets[x]:
        if country_sets[x][y]["free"] == country_sets[x][z]["free"]:
          isomorphic_countries[y]["free"].append(z)
        if country_sets[x][y]["onarrival"] == country_sets[x][z]["onarrival"]:
          isomorphic_countries[y]["onarrival"].append(z)
        if country_sets[x][y]["required"] == country_sets[x][z]["required"]:
          isomorphic_countries[y]["required"].append(z)
        if country_sets[x][y]["refused"] == country_sets[x][z]["refused"]:
          isomorphic_countries[y]["refused"].append(z)
  # print country_sets["Africa"]["Zimbabwe"]
  # print isomorphic_countries["Sweden"]
  isom_classes = {}
  isom_classes["free"] = [(x,isomorphic_countries[x]["free"]) for x in [c for c in isomorphic_countries if len(isomorphic_countries[c]["free"])>1]]
  isom_classes["onarrival"] = [(x,isomorphic_countries[x]["onarrival"]) for x in [c for c in isomorphic_countries if len(isomorphic_countries[c]["onarrival"])>1]]
  isom_classes["required"] = [(x,isomorphic_countries[x]["required"]) for x in [c for c in isomorphic_countries if len(isomorphic_countries[c]["required"])>1]]
  isom_classes["refused"] = [(x,isomorphic_countries[x]["refused"]) for x in [c for c in isomorphic_countries if len(isomorphic_countries[c]["refused"])>1]]

def create_pairwise_networks(nodes, links):
  pairwise_nodes = {}
  pairwise_links = {}
  for a in CONTS:
    for b in CONTS:
      pairwise_links[a + "-" + b] = []
      for t in links:
        for l in links[t]:
          if (l["source"]["continent"] == a and l["target"]["continent"] == b): 
            source_node = {"name": l["source"]["name"], "continent": l["source"]["continent"] , "type": "origin", "y": l["source"]["y"]}
            target_node = {"name": l["target"]["name"], "continent": l["target"]["continent"] , "type": t, "y": l["target"]["y"]}
            term = l["term"]
            notes = l["notes"]
            pairwise_links[a + "-" + b].append({"source": source_node, "target": target_node, "term": term , "notes": notes})
      pairwise_nodes[a + "-" + b] = []    
      for d in CONTS[a]:      
        pairwise_nodes[a + "-" + b].append({"name": d, "continent": a, "type": "origin", "y": nodes[d][1]})         
      for l in pairwise_links[a + "-" + b]:
        if l["target"] not in pairwise_nodes[a + "-" + b]:
          pairwise_nodes[a + "-" + b].append(l["target"])
  #print len(pairwise_nodes[("North America-Africa")])#, pairwise_nodes[("North America-Africa")][:10]
  return (pairwise_nodes, pairwise_links)

def find_reciprocal_network(nodes, links, countries, status):
  #frees = []
  couples = {}
  recip_nodes = {}
  recip_links = {}
  for x in links[status]:
    #frees.append(x["source"]["name"])
    if (x["source"]["name"]+"-"+x["target"]["name"]) in couples.keys():
      couples[x["source"]["name"]+"-"+x["target"]["name"]] += 1
      couples[x["target"]["name"]+"-"+x["source"]["name"]] += 1
    else:
      couples[x["source"]["name"]+"-"+x["target"]["name"]] = 1
      couples[x["target"]["name"]+"-"+x["source"]["name"]] = 1
  recip_network = sorted(list(set(["-".join(sorted(y.rsplit("-", 1))) for y in couples.keys() if couples[y] == 2])))
  recip_ranked = sorted([(c, len([n for n in recip_network if (c in n)])) 
    for c in sorted(list(set([y.rsplit("-", 1)[0] 
      for y in couples.keys() if couples[y] == 2]))
    )
  ], key=lambda x: x[1], reverse=True)
  for c in CONTS:
    recip_nodes[c] = []
    for i in [x for x in CONTS[c] if x in [s[0] for s in recip_ranked]]:
      recip_nodes[c] += [n for n in nodes if n["name"] == i]
  for d in CONTS:
    recip_links[d] = []
    for j in [y.rsplit("-", 1) for y in [z for z in couples if couples[z] == 2] if y.rsplit("-", 1)[0] in CONTS[d]]:
      recip_links[d].append({"source": [n for n in recip_nodes[d] if n["name"]==j[0]][0], "target": [n for n in recip_nodes[countries[j[1]][0]] if n["name"]==j[1]][0]})
  print make_source_dicts_from_recip(recip_nodes, recip_links)
  return {"nodes": recip_nodes, "links": recip_links}
  #return recip_network
  #return recip_ranked

def make_source_dicts_from_recip(nodes, links):
  network = {}
  for source_cont in CONTS:
    network[source_cont] = {"nodes": [], "links": []}
    network[source_cont]["nodes"] += [x for y in [nodes[z] for z in nodes] for x in y]
    network[source_cont]["nodes"] += [{"name": x["name"], "y": x["y"], "continent": "Origin"} for x in nodes[source_cont]]
    network[source_cont]["links"] += [{"source": {"name": l["source"]["name"], "y": l["source"]["y"], "continent": "Origin"}, "target": l["target"]} for l in links[source_cont]]
    #print network[source_cont]["nodes"][-1], network[source_cont]["links"][0]
  return json.dumps(network)

def make_graph(list_of_edges):
  G = nx.Graph()
  for x in list_of_edges:
    pair = tuple(x.split("-", 1))
    G.add_edge(pair[0], pair[1])
  print len(G.edges())
  pos=nx.fruchterman_reingold_layout(G)
  nx.draw(G,pos)
  plt.show()
  return len(list_of_edges)


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
  #print len(links["free"])
  find_reciprocal_network(nodes, links, countries, "free")
  # for t in find_reciprocal_network(nodes, links, countries, "free"):
  #   print t
  #print find_reciprocal_network(nodes,links,countries,"free")
  #print make_graph(find_reciprocal_network(nodes, links, countries, "free"))
  pair_dicts = create_pairwise_networks(countries, links)
  # print pair_dicts[1][("North America-Oceania")], len(pair_dicts[1][("North America-Oceania")])
  return json.dumps({"pairwise_nodes": pair_dicts[0], "pairwise_links": pair_dicts[1]})
  #return json.dumps({"nodes": nodes, "links": links[output_key]}) 

'''CL arguments are data_folder and output_key'''
if __name__=="__main__":
  main(sys.argv[1])
  # print create_continents_dictionary()