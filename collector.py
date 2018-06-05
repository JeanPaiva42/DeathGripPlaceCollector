#Recomendo rodar o script no console do python

import json
import requests as re
from math import sin, cos, sqrt, atan2, radians
import pandas as pd
from pandas import DataFrame

#função que calcula a distancia da lat e lon
def getDist(lat2, lon2):
    R = 6373.0
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

#Função que gera o próximo centro de busca de lugares
def getNextLocation(oi):
    try:
        results = oi.json()['results']
        lat2 = radians(results[0]['geometry']['location']['lat'])
        lon2 = radians(results[0]['geometry']['location']['lng'])
        dist = getDist(lat2,lon2)
        tam = len(results)
        maisLonge = 0
        for i in range(1, tam):
            lat2 = radians(results[i]['geometry']['location']['lat'])
            lon2 = radians(results[i]['geometry']['location']['lng'])
            dist2 = getDist(lat2, lon2)
            if(dist2 >= dist):
                dist = dist2
                maisLonge = i
    except:
        print("Não foi possível extrair novos dados, verifique o limite da API")
        pass
    return (results[maisLonge]['geometry']['location']['lat'],
            results[maisLonge]['geometry']['location']['lng'])



#capitais_br = #['Rio Branco', 'Maceió', 'Macapá', 'Manaus', 'Salvador', 'Fortaleza', 'Brasília', 'Vitória', 'Goiânia', 'São Luís', 'Cuiabá', 'Campo Grande', 'Belo Horizonte', 'Belém', 'João Pessoa', 'Curitiba', 'Recife', 'Teresina', 'Rio de Janeiro','Porto Alegre', 'Porto Velho', 'Boa Vista', 'Florianópolis', 'São Paulo', 'Aracaju', 'Palmas']


#Insira nessas lista o nome das cidades que deseja obter os place_id
capitais_br = ['Maripá de Minas, MG']
for p in capitais_br:
    api_key = ''

    #Procurao lugar e recupera as coordenadas
    place = p
    url_place = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+place+'&key='+api_key
    #pegando as coordenadas iniciais do lugar
    get_coordinates = re.get(url_place)

    location = get_coordinates.json()['results'][0]['geometry']
    initial_lat = str(location['location']['lat'])
    initial_lon = str(location['location']['lng'])
    ##
    #começando a primeira procura
    radius = 2000
    url = 'https://maps.googleapis.com/maps/api/place/radarsearch/json?' \
          'location='+initial_lat+','+initial_lon+'&radius='+str(radius)+'&type=establishment&key=' + api_key
    resposta = re.get(url)
    lat1 = radians(float(initial_lat))
    lon1 = radians(float(initial_lat))

    final = []
    strike = 0
    t_coord = (float(initial_lat),float(initial_lon))
    while len(final)<40:
        #vai atualizando o próximo lugar
        if strike == 3:
            break
        t_coord_aux = getNextLocation(resposta)
        if t_coord_aux == t_coord:
            radius+=500
            initial_lat, initial_lon = t_coord_aux
            strike+=1
        else:
            initial_lat, initial_lon = t_coord_aux
            t_coord = t_coord_aux
            strike = 0

        url = 'https://maps.googleapis.com/maps/api/place/radarsearch/json?' \
              'location='+str(initial_lat)+','+str(initial_lon)+'&radius='+str(radius)+'&type=establishment&key=' + api_key
        print(initial_lat, initial_lon)
        try:
            resposta = re.get(url)
            final.append(resposta.json()['results'])
        except:
            print('falha em obter resultados, checar limite de requisições da api')

    #append as lista tudo
    final = [j for i in final for j in i]
    list_df = []
    for i in final:
        aux_list = []
        aux_list.append(i['geometry']['location']['lat'])
        aux_list.append(i['geometry']['location']['lng'])
        aux_list.append(i['id'])
        aux_list.append(i['place_id'])
        aux_list.append(i['reference'])
        list_df.append(aux_list)

    #arrumando os dados para criar o .csv

    headers = ['lat', 'lng', 'id', 'place_id', 'reference']


    #criando dataframe, limpando

    df = DataFrame(list_df, columns=headers)
    df = df.drop_duplicates(subset=['place_id'], keep='first')
    df.to_csv(place+'_places_id', sep=',', encoding='utf-8')
    print(place+ " "+str(df.shape))




