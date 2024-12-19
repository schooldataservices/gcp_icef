import os
json_file_path =  '/home/g2015samtaylor/icef-437920.json'

#All BQ tables that are begin queryed are the keys. 
#How they are saved in the local dir are the values
iready_dictionary = {'diagnostic_results_ela_CONFIDENTIAL.csv':'diagnostic_results_ela.csv',
                    'diagnostic_results_math_CONFIDENTIAL.csv':'diagnostic_results_math.csv',
                    
                    }

#make sure to put the extension names on the files, and have the naming convention of the variables exact
sftp_configs = [
    # {
    #     'sftp_type': 'clever_import',
    #     'local_sftp_type': 'iota_sftp',
    #     'import_or_export': 'import',
    #     'target_sftp_folder_name': '/idm-sensitive-exports',
    #     'local_sftp_folder_name': '/powerschool_combined', 
    #     'export_local_bq_replications': False,
    #     'project_id':'powerschool-420113'
    # },

    # --------------------------------

    # {
    #     'sftp_type': 'clever_export',
    #     'local_sftp_type': 'iota_sftp',
    #     'import_or_export': 'export',
    #     'target_sftp_folder_name': '/home/boundless-calendar-0789', 
    #     'local_sftp_folder_name': '/bq_replications/clever_iota_file_transfer',
    #     'naming_dict': clever_dictionary,
    #     'db':'roster_files',
    #     'export_local_bq_replications': True,
    #     'project_id':'powerschool-420113'
    # },
    # ----------------------------------

    {
        'sftp_type': 'iready_import',
        'local_sftp_type': 'local_sftp', #must follow naming convention in .json file
        'import_or_export': 'import',
        'target_sftp_folder_name': '/exports/Current_Year/',
        'local_sftp_folder_name': '/iready', 
        'files_to_download': ['diagnostic_results_ela_CONFIDENTIAL.csv', 'diagnostic_results_math_CONFIDENTIAL.csv'],
        'naming_dict': iready_dictionary,  
        'export_local_bq_replications': False,
        'project_id':'icef-437920'
    },

    # -------------------------------------

    # {
    #     'sftp_type': 'savva_export',
    #     'local_sftp_type': 'iota_sftp',
    #     'import_or_export': 'export',
    #     'target_sftp_folder_name': '/SIS',
    #     'local_sftp_folder_name': '/bq_replications/savva_iota_file_transfer',
    #     'naming_dict': savva_dictionary,
    #     'db': 'roster_files',
    #     'export_local_bq_replications': True, 
    #     'project_id':'powerschool-420113'
    # }
     # --------------------------------
]


