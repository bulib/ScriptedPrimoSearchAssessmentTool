## spst.py
class Spst:
    '''Functions to support Scripted Primo Search Tool'''
    # prod_url = <base url>
    prod_url_base = 'http://bu-primo.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
    # stage_url = <base url>
    stage_url_base = 'http://bu-primostage.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
    ## query params ##
    query_Params1 = '?institution=BOSU&query=any,contains,'
    query_Params2 = '&indx=1&bulkSize=2'
    query_Params3 = '&loc=local,scope:(BOSU)&loc=adaptor,primo_central_multiple_fe&onCampus=true&json=true'
    def __init__(self):
        return 
    # build_url 
    # takes base_url and search_string, returns url properly formated for searching
    def build_url(self,platform,search_string):
        if platform == 'prod':
            base_url = Spst.prod_url_base
        else:
            base_url = Spst.stage_url_base
        url = base_url+Spst.query_Params1 + search_string.replace(' ','+') + Spst.query_Params2 + Spst.query_Params3
#        print(url)
        return(url)

    def parse_response(search,response,platform,search_no):
        '''parse_response takes response (as json) from search, 
        returns response_dict (dict of our responses)
        Parameters:  
            search: the search string
            response: the json response from Primo
            platform: production or stage
            search_no: the number of the search performed
        '''
        response_dict = {}
        # define the elements to grab from the json response. These become the columns in the dataframe
        elements = []
        #elements.append('Platform')
        #elements.append('Search')
        #elements.append('ResultNumber')
        #elements.append('TotalHits')
        #elements.append('Rank')
        #elements.append('SearchEngine')
        elements.append('control.recordid')
        elements.append('display.type')
        elements.append('display.creator')
        elements.append('display.title')
        elements.append('display.ispartof')
        elements.append('delivery.delcategory')
        elements.append('delivery.fulltext')
        elements.append('search.searchscope')
        elements.append('search.general')
        elements.append('facets.collection')
        elements.append('facets.frbrtype')
        elements.append('facets.toplevel')
        elements.append('facets.prefilter')
        elements.append('sort')
        # parse the response to return the data desired elements
        response = json.loads(response.decode('utf8'))
        # need to extract the desired elements and add them to a dict
        response = response['SEGMENTS']
        response = response['JAGROOT']
        response = response['RESULT']
        response_dict['facet'] = response['FACETLIST']
        response_dict['docset'] = response['DOCSET']
        docs = response_dict['docset']['DOC']
        facets = response_dict['facet']

        ## define a dataframe to return the results
        doc_columns = ['Platform','Search_No','Search','ResultNumber','TotalHits','FirstHit','LastHit','Rank','SearchEngine','recordid', \
               'type','creator','title','ispartof','delcategory','fulltext','searchscope','general','collection', \
              'frbrtype','toplevel','prefilter','sort']
        df_doc = pd.DataFrame(columns = doc_columns)
        fac_columns = ['Platform','Search_No','Search','TotalHits','SearchEngine','facet','values']
        df_facets = pd.DataFrame(columns = fac_columns)
        #bib = doc['PrimoNMBib']['record']
        #print(type(bib)
        ## iterate through the results (normally 10) to populate a dictionary that will be added to the dataframe
        for doc in docs:
            doc_dict = {}
            doc_dict['Platform'] = platform
            doc_dict['Search_No'] = search_no
            doc_dict['Search'] = search
            doc_dict['ResultNumber'] = doc['@NO']
            doc_dict['TotalHits'] = response['DOCSET']['@TOTALHITS']
            doc_dict['FirstHit'] = response['DOCSET']['@FIRSTHIT']
            doc_dict['LastHit'] = response['DOCSET']['@LASTHIT']
            doc_dict['Rank'] = doc['@RANK']
            doc_dict['SearchEngine'] = doc['@SEARCH_ENGINE']
            #doc_dict['Bib'] = doc['PrimoNMBib']['record']
            Bib = doc['PrimoNMBib']['record']

            for element in elements:
                x = element.split('.')
                if len(x) == 1:
                    try:
                        doc_dict[x[-1]] = Bib[x[0]]
                    except:
                        pass
                if len(x) == 2:
                    try:
                        doc_dict[x[-1]] = Bib[x[0]][x[1]]
                    except:
                        pass
                if len(x) == 3:
                    try:
                        doc_dict[x[-1]] = Bib[x[0]][x[1]][x[2]]
                    except:
                        pass
                if len(x) == 4:
                    try:
                        doc_dict[x[-1]] = Bib[x[0]][x[1]][x[2]][x[3]]
                    except:
                        pass
                if len(x) == 5:
                    try:
                        doc_dict[x[-1]] = Bib[x[0]][x[1]][x[2]][x[3]][x[4]]
                    except:
                        pass   
            df_doc = df_doc.append(doc_dict, ignore_index=True)
            #print(doc_dict)
            f_dict = parse_facets(facets['FACET'])
            for k,v in f_dict.items() :
                if doc['@NO'] == '1':
                    facet_dict = {}
                    facet_dict['Platform'] = platform
                    facet_dict['Search_No'] = search_no
                    facet_dict['Search'] = search
                    #facet_dict['ResultNumber'] = doc['@NO']
                    facet_dict['TotalHits'] = response['DOCSET']['@TOTALHITS']
                    facet_dict['SearchEngine'] = doc['@SEARCH_ENGINE']
                    facet_dict['facet'] = k
                    facet_dict['values'] = v
                    df_facets = df_facets.append(facet_dict,ignore_index=True)

        return(df_doc,Bib,df_facets)

    def parse_facets(facets):
        '''
        parse_facets returns a dictionary of the facets and facet values from the
        facet section of the Primo response (json)
        Parameters:
            facets: the facet section of the Primo response
        '''
        return_dict = {}
        for facet in facets:
            f = facet['@NAME']
            fv = facet['FACET_VALUES']
            #print(f)
            l = []
            for x in fv :
                try:
                    l.append((x['@KEY'],int(x['@VALUE'])))
                except Exception as e:
                    pass
            sorted_by_second = sorted(l, key=lambda tup: tup[1],reverse=True)
            return_dict[f] = sorted_by_second
        return return_dict

