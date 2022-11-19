# -*- coding: utf-8 -*-


def clean_data_frame(df):
    """
    Removes columns whose values are python objects and returns a 
    dictionary of dataframes
    """
    
    id_col = df.columns[0]
    if 'id' not in id_col:
        id_col = df.index.name or ''
        if 'id' in id_col:
            df = df.reset_index()
        else:
            raise Exception('Bad ID Col')
    
    # Remove leading underscores from column names and replace
    # periods with underscores
    df.columns = [x[1:] if x.startswith('_') else x for x in df.columns]
    df.columns = [x.replace('.','_') for x in df.columns]
    
    # Create dictionary of column names and first real values
    cols_dict = {}
    for col in df:
        idx = df[col].first_valid_index()
        cols_dict.update({col: df[col].iloc[idx or 0]})
    del cols_dict[id_col]
    
    # Cols to rename to reddit_obj_id
    fullnamekeys = {'t1_' : 'comment',
                    't2_' : 'account',
                    't3_' : 'post',
                    't4_' : 'message',
                    't5_' : 'subreddit',
                    't6_' : 'award'}
    rename_dict = {}
    for key, obj_name in fullnamekeys.items():
        for col, value in cols_dict.items():
            if isinstance(value, str) and value.startswith(key):
                parent = ''
                if 'parent' in col:
                    parent = 'parent_'
                rename_dict[col] = f'{parent}reddit_{obj_name}_id'
    for key, value in rename_dict.items():
        cols_dict[value] = cols_dict[key]
        del cols_dict[key]
                
    df = df.rename(columns=rename_dict)
    
    # Break out dataframe into columns whose values are classes, iterables,
    # and all else
    class_cols = [id_col]
    iter_cols = [id_col]
    keep_cols = [id_col]
    for col, value in cols_dict.items():
        is_iterable = hasattr(value, '__iter__') and not isinstance(value, str)
        is_class = hasattr(value, '__module__')
        if is_class:
            class_cols.append(col)
        elif is_iterable:
            iter_cols.append(col)
        else:
            keep_cols.append(col)
    
    # Return dictionary of dataframes
    return {'cleaned_dataframe' : df[keep_cols].set_index(id_col),
            'iterables'         : df[iter_cols].set_index(id_col),
            'obejcts'           : df[class_cols].set_index(id_col)}



