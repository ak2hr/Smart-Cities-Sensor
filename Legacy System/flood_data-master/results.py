import pandas as pd
from hr_db_scripts.main_db_script import get_db_table_as_df
from db_scripts.main_db_script import db_filename, fig_dir

def make_results_df(models=['poisson', 'rf'], types=['train', 'test'], 
        metrics=['RMSE', 'MAE', 'std'], suffix='revisions1', filter_nz=True):
    combinations = ['{}-{}'.format(x, y) for x in metrics for y in types]
    data_dict = {a:[] for a in combinations}
    for m in models:
        for t in types:
            table_name = '{}_{}_{}'.format(m.lower(), suffix, t)
            print m, t, table_name
            df = get_db_table_as_df(table_name, dbfilename=db_filename)
            true_col = 'all_trn' if t == 'train' else 'all_tst'
            pred_col = true_col.replace('_', '_pred_')
            df = df[[true_col, pred_col]]
            df = df[df[pred_col] <= 159]
            if filter_nz:
                df = df[df[true_col] > 0]
            data_dict['RMSE-' + t].append((((df.iloc[:, 0] - df.iloc[:, 1])**2).mean())**0.5)
            data_dict['MAE-' + t].append((abs(df.iloc[:, 0] - df.iloc[:, 1])).mean())
            grouped = df.groupby(true_col)
            mean_range = (grouped.std()).mean().values[0]
            data_dict['std-' + t].append(mean_range)

    df = pd.DataFrame(data_dict, index=models)
    df = df[combinations]
    df.columns = df.columns.str.replace('train', 'Training')
    df.columns = df.columns.str.replace('test', 'Evaluation')
    df = df.round(2)
    return df
