
## spst.py
import json

class SPST:
    '''Functions to support Scripted Primo Search Tool
    Instance variables:
    url_base = 'http://bu-primo.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
    platform = 'production'
    scope = '&loc=local,scope:(BOSU)&loc=adaptor,primo_central_multiple_fe'
    onCampus = 'onCampus'
    
    Class variables
    bulkSize = '10'
    onCampus = 'true'
    institution = 'BOSU'
    search_strings = []
    '''
    import pandas as pd
    import pymarc
    import marcx

    ##    Class variables
    bulkSize = '10'
    onCampus = 'true'
    institution = 'BOSU'
    search_strings = []

    def __init__(self):
        ## Instance Variables
        platform = 'production'
        url_base = 'http://bu-primo.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
        scope = '&loc=local,scope:(BOSU)&loc=adaptor,primo_central_multiple_fe'
        #stage_url_base = 'http://bu-primostage.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
        return 
    
    def set_platform_scope(self,d):
        '''
        Function: set_platform_scope
        Parameters: dictionary containing keys: 'platform','scope', and/or 'url_base'
        The function sets the platform and scope variables and adjusts the 'url_base' variable to match the platform
        '''
        if 'platform' in d.keys():
            self.platform = d['platform']
        if 'scope' in d.keys():
            self.scope = d['scope']
        if 'url_base' in d.keys():
            self.url_base = d['url_base']
        elif self.platform.lower() == 'production':
            self.url_base = 'http://bu-primo.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
        elif self.platform.lower() == 'stage':
            self.url_base = 'http://bu-primostage.hosted.exlibrisgroup.com:1701/PrimoWebServices/xservice/search/brief'
        else:
            pass
        return

    @classmethod
    def set_search_strings(cls,f,t_a):
        '''
        Parameters: 
        f = the path of the file to open that contains the search strings. This can be a 'csv' or marcxml 'xml' file. The file
        extsion is used to determine how to process the file.
        t_a = the type of file string to create. This is most relevant for marcxml files. The file string can be constructed
        to include just the title or the title and author. Appropriate values include: 'title' and 'title_author'
        '''
        import pymarc
        import marcx
        import io
        import pandas as pd
        if (f[-3:]) == 'csv':
            cls.search_strings = open(f).read().splitlines()
        if (f[-3:]) == 'xml':
            records = pymarc.parse_xml_to_array(io.open(f,mode='r',encoding='utf-8'))
            df_search = pd.DataFrame()
            for rec in records:
                d = {}
                rec = marcx.FatRecord.from_record(rec)
                try:
                    d['author'] = rec['100']['a']
                except Exception as e:
                    d['author'] = ''
                d['title'] = rec.title() #.replace('/','')
                d['mmsid'] = rec['001'].data
                d['title_author'] = rec.title() #.replace('/','') + ' ' + d['author'] #rec.author()
                df_search = df_search.append(d,ignore_index=True)
            if t_a == None:
                t_a = 'title'
            if t_a == 'title_author':
                cls.search_strings = df_search['title_author']
            else:
                cls.search_strings = df_search['title']




    @classmethod
    def set_params(cls,bsize,oCampus,inst):
        cls.bulkSize = bsize
        cls.onCampus = oCampus
        cls.institution = inst
    
    # build_url 
    # returns url properly formated for searching
    def build_url(self,search_string):
        '''Returns properly formatted url for each search string based on defined variables in the class'''
        query_Params1 = '?institution=' + SPST.institution + '&query=any,contains,'
        query_Params2 = '&indx=1&bulkSize=' + SPST.bulkSize
        query_Params3 = self.scope + '&onCampus=' + self.onCampus + '&json=true'
        url = self.url_base+query_Params1 + search_string.replace(' ','+') + query_Params2 + query_Params3
        return(url)

    def parse_response(self,search,response,platform,search_no):
        '''parse_response takes response (as json) from search, 
        returns response_dict (dict of our responses)
        Parameters:  
            search: the search string
            response: the json response from Primo
            platform: production or stage
            search_no: the number of the search performed
        '''
        import json
        import pandas as pd
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
        #elements.append('addata.doi')
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
        doc_columns = ['Platform','Search_No','Search','ResultNumber','TotalHits','FirstHit','LastHit','Rank','SearchEngine','recordid', 'doi','OpenURL','linktorsrc',\
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
            try:
                doc_dict['OpenURL'] = doc['LINKS']['openurlfulltext']
                
            except Exception as e:
                pass
            try:
                doc_dict['doi'] = 'https://dx.doi.org/'+doc['PrimoNMBib']['record']['addata']['doi']
                
            except Exception as e:
                pass
            try:
                doc_dict['linktorsrc'] = doc['LINKS']['linktorsrc']
            except Exception as e:
                pass
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
            x = '' ## dummy variable when calling from within the class
            f_dict = SPST.parse_facets(facets['FACET'])
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
        
    def data(self,*args, **kwargs):
        import pandas as pd
        import time
        from urllib.request import Request, urlopen
        from urllib.parse import urlencode, quote_plus
            # Create a dataframe with
            # - column for search string 
            # - column for response (returned from parse_response fuction)
        columns = ['Platform','Search','ResultNumber','TotalHits','FirstHit','LastHit','Rank','SearchEngine','recordid', \
                    'type','creator','title','ispartof','delcategory','fulltext','searchscope','general','collection', \
                    'frbrtype','toplevel','prefilter','sort']
        df = pd.DataFrame(columns = columns)
        fac_columns = ['Platform','Search_No','Search','TotalHits','SearchEngine','facet','values']
        df_f = pd.DataFrame(columns = fac_columns)
        counter = 0
        begin = kwargs.get('start', 0)
        end = kwargs.get('end', len(SPST.search_strings))
        for search_string in SPST.search_strings[begin:end]:
            time.sleep(0.5)
            if counter%100 == 0:
                print('Processed: ',str(counter),' searches on ',self.platform)
            search_url = self.build_url(search_string)
            request = Request(search_url)
            try:
                response_body = urlopen(request).read()
                d = SPST.parse_response(self,search_string,response_body,'production',counter)[0]
                b = SPST.parse_response(self,search_string,response_body,'production',counter)[1]
                f = SPST.parse_response(self,search_string,response_body,'production',counter)[2]
                df = df.append(d, ignore_index=True)
                df_f = df.append(f, ignore_index=True)
            except Exception as e:
                pass
            counter += 1  
        print('Processed: ',str(counter),' searches on ',self.platform)
        return(df) #,df_f)
    
class CompResults:
    '''
    Function: compare_platforms
    Purpose:  compare the search results of two platforms (production and staging) passed as dataframes
    Parameters: 
       p - dataframe containing the search results from first (production) search
       s - dataframe containing the search results from second (stage) search
       columns - (optional) list of columns to be returned in the results compared dataframe
       index - (optional) column or list of columns to be used to index the results
    '''


    def __init__(self):
        ## Instance Variables
        return 

    def Compare2ResultSets(self,p,s,*args, **kwargs):
        import pandas as pd
        import itertools
    
        results_df = pd.DataFrame()
        cols = ['match','Recordid','Rank','Collection','Creator',
                'Delcategory','Frbrtype','Fulltext','Title','Toplevel','Type']
        columns = kwargs.get('columns', cols)
        indx = ['Search', 'ResultNumber']
        index = kwargs.get('index', indx)
        if (type(p) != pd.core.frame.DataFrame) and (type(s) != pd.core.frame.DataFrame):
            raise TypeError('Expected production and stage parameters to be dataframes')
        p = p.set_index(index)
        p = p[columns]
        s = s.set_index(index)
        s = s[columns]
        ## preface the column label with 'p' or 's' to designate the platform
        p.columns = ['P'+ x for x in p.columns]
        p.columns = [label[0:1].lower() + label[1:2].upper() +label[2:] for label in p.columns]
        s.columns = ['S'+ x for x in s.columns]
        s.columns = [label[0:1].lower() + label[1:2].upper() +label[2:] for label in s.columns]
        ret_cols = list(itertools.chain(*[['P'+x,'S'+x] for x in columns]))  
        ret_cols = [label[0:1].lower() + label[1:2].upper() +label[2:] for label in ret_cols]
        ret_cols.append('Search')
        ret_cols.append('ResultNumber')
        ret_cols.append('match')
        results_df = pd.DataFrame(columns = ret_cols)
        for i,row in s.iterrows():
            d = {}
            d['Search'] = i[0]
            d['ResultNumber'] = i[1]
            for col in s.columns:
                pcol = 'p' + col[1:]
                if col == 'sRecordid':
                    if row['sRecordid'] == p.loc[i]['pRecordid']:
                        d['match'] = True
                    else:
                        d['match'] = False
                d[col] = row[col]
                d[pcol] = p.loc[i][pcol]
            results_df = results_df.append(d,ignore_index=True)
        results_df = results_df.set_index(index)
            
        return(results_df)
        
        
        

