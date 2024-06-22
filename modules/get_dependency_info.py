import pandas as pd

def get_dependencies_formatted_for_graph(df):
    """
    Formats a DataFrame containing tasks and their dependencies into a list of dictionaries
    suitable for use in a force-directed graph.

    Args:
        df (pd.DataFrame): DataFrame with columns 'task_name' and 'depends_on'.
                           'task_name' contains the name of the task.
                           'depends_on' contains dependencies as a string.

    Returns:
        list: A list of dictionaries, each containing 'item' and 'dependencies' keys.
    """
    items = []
    for i, row in df.iterrows():
        item = {
            "item": row['task_name'],
            "dependencies": row['depends_on']
        }
        items.append(item)
    return items

if __name__ == '__main__':
    # Example usage
    df = pd.DataFrame({
        'dag': ['a', 'b', 'c'],
        'task_name': ['task1name', 'task2name', 'task3name'],
        'task': ['task1', 'task2', 'task3'],
        'args': ['client_arg', 'none', 'client_arg'],
        'depends_on': ['', '{task1,task3}', '']
    })
    print(get_dependencies_formatted_for_graph(df))
    # [{'item': 'task1name', 'dependencies': ''}, {'item': 'task2name', 'dependencies': '{task1,task3}'}, {'item': 'task3name', 'dependencies': ''}]
