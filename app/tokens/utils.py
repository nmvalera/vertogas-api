import pandas as pd


def insert_table(path, table_name, con):
    table = pd.read_pickle(path)
    table.to_sql(table_name, con, index_label='id', if_exists='append')
