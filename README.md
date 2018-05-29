# World Event in Wikipedia

Wiki_data_collections_all.py includes all the python code that can be reused: 
 
- GetRevisions: collection all revisions for a specific article, check https://www.mediawiki.org/wiki/API:Revisions for other useful variables to self define useful API (e.g., size, time, editor, etc.)

- GetUserContri: collection all contributions for a specific user given his/her Wikipedia user name, check https://www.mediawiki.org/wiki/API:Usercontribs for other useful variables to self define useful API (e.g., size, time, editor, etc.)

Wiki_Quality_doc.py includes sample codes and comments of: 

- Collecting "reverted revision" using mwrevert.api (https://github.com/mediawiki-utilities/python-mwreverts/blob/master/ipython/basic_usage.ipynb) [sample paper to understand the revert as quality measures in Wikipedia: https://dl.acm.org/citation.cfm?id=2038585]

- Collecting the revision good-faith quality score using ORES (https://ores.wikimedia.org/v3)
