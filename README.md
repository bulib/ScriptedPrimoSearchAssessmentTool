# ScriptedPrimoSearchAssessmentTool
### version 1.0.7

##Purpose:
SPST is a tool to automate searching Ex Libris Primo using a set of search strings for the purpose of comparison and analysis. The core functionality of SPST is to iterate through a list of search strings, sending a Deep Link Query to Primo, returning the results in a Pandas dataframe.

Originally conceived as a tool to automate efforts to compare the impact of activating various collections in Primo Central Index, the number of use cases has begun to grow. The tool is currently being developed to enable the Libraries in:

* Assessing the impact of activating particular Primo Central Index collections on the user search experience
* Identifying problems with deduping and FRBRizing
* Assessing issues in known item searching


##Classes
Two classes are included:

SPST: has several functions that do that searching

* 	set_platform_scope
* 	set_search_strings
* 	set_params
* 	build_url
* 	parse_response
* 	parse_facets (haven’t done much with this yet)
* 	get_data (performs the searches)

CompResults: has functions that do the comparison and analysis (only one so far)

* Compare2ResultSets

##Documentation
SPST is still being developed and documentation is rather sparse. The SPST_Demo.ipynb python notebook provides examples that will hopefully assist in getting started. 

##Installation

pip install git+https://github.com/jwacooks/ScriptedPrimoSearchAssessmentTool.git


jammerman
2016-01-19



  
