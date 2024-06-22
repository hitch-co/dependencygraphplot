import sys
import os
import pandas as pd

# Imported packages
sys.path.append(os.path.abspath('C:/_repos/redshift_query_runner'))
from RedshiftQueryRunner import query_runner

# Primary classes/modules in this repo
from classes.dependencygraphplot import ForceDirectedGraph
from modules.get_dependency_info import get_dependencies_formatted_for_graph

############################################
# Set some variables
base_dir = os.getcwd()
yaml_filepath = os.path.join(base_dir, 'config/config.yml')
sql_filepath = os.path.join(base_dir, 'sql/dag_tasks.sql')

# Set some variables
dag_client_names = ['murad']
timezone = {'timezone': 'EDT'}

############################################
# Create an instance of the query_runner class
runner = query_runner(
    os.path.join(base_dir,yaml_filepath), 
    environment='production', 
    password_envvar='PRIV_REDSHIFT_PASSWORD'
    )

df_tasks = runner.query_dag_tasks_from_file_to_dataframe(
    os.path.join(sql_filepath),
    colname='dag',
    values=dag_client_names,
    timezone=timezone
)
df_tasks.to_csv('files/df_tasks.csv', index=False)


####################################################
# Create items list and an instance of the ForceDirectedGraph class
dependencies_formatted = get_dependencies_formatted_for_graph(df_tasks)
graph = ForceDirectedGraph(dependencies_formatted)
response = graph.run()

####################################################
#write to csv
df = pd.DataFrame(response)
df.to_csv('files/df_response.csv', index=False)