import argparse
import os
import pandas as pd

MAPPED_KEYS = {"DE":"DE", "DK":"DK", "HU":"HU", "IT":"IT", "NE":"NL", "PO":"PO", "SE":"SE", "SP":"SP", "UK":"UK", "NL":"NL"}

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

def clean_data(generated, load, save_raw):
    # TODO: Handle missing values, outliers, etc.
    generated['StartTime'] = generated['StartTime'].str.rstrip('Z')
    generated['EndTime'] = generated['EndTime'].str.rstrip('Z')
    # Convertir las columnas StartTime y EndTime a tipo datetime sin especificar formato
    generated['StartTime'] = pd.to_datetime(generated['StartTime'])
    generated['EndTime'] = pd.to_datetime(generated['EndTime'])

    # Redondear las fechas a la hora más cercana
    generated['HourlyTime'] = generated['StartTime'].dt.round('H')

    generated_clean = generated.groupby(['HourlyTime', 'Country']).agg({
        'UnitName': 'first',
        'quantity': 'sum'
    }).reset_index()

    load['StartTime'] = load['StartTime'].str.rstrip('Z')
    load['EndTime'] = load['EndTime'].str.rstrip('Z')

    load['StartTime'] = pd.to_datetime(load['StartTime'])
    load['EndTime'] = pd.to_datetime(load['EndTime'])

    load['HourlyTime'] = load['StartTime'].dt.round('H')

    load_clean = load.groupby(['HourlyTime', 'Country']).agg({
        'UnitName': 'first',
        'Load': 'sum'
    }).reset_index()

    df = pd.merge(generated_clean, load_clean, on=['HourlyTime', 'Country'], how='inner', suffixes=('Gen', 'Load'))

    return df


def preprocess_data(df):
    # TODO: Generate new features, transform existing features, resampling, etc.
    df = df.drop(columns=['UnitNameGen', 'UnitNameLoad'])
    
    df_pivoted = df.pivot(index='HourlyTime', columns='Country', values=['quantity', 'Load'])
    df_pivoted.columns = ['{}_{}{}'.format(col[0], col[1], '' if len(col) < 3 else col[2]) for col in df_pivoted.columns]
    new_columns = []
    print(df_pivoted.columns)
    for col in df_pivoted.columns:
        if col == 'HourlyTime':
            new_columns.append(col)
        elif 'quantity' in col:
            new_columns.append('green_energy_{}'.format(col.split("_")[-1]))
        else:
            new_columns.append('{}_Load'.format(col))

    df_pivoted.columns = new_columns

    return df_pivoted


def save_data(df, output_file):
    df.to_csv(output_file, index=True)
    return

def process_nans(df, column):
    df[column] = df[column].fillna((df[column].shift() + df[column].shift(-1)) / 2)
    return df


def unify_data(data_path):
    generated = {}
    load = {}
    for key in MAPPED_KEYS:
        generated[key] = []
    
    file_list = os.listdir(data_path)
    for file in file_list:
        file_path = os.path.join(data_path, file)
        if os.path.isfile(file_path):
            if "gen" in file_path:
                df = load_data(file_path=file_path)
                df =process_nans(df, column="quantity")
                country = file.split("_")[1]
                generated[MAPPED_KEYS[country]].append(df)
            elif "load" in file_path:
                df = load_data(file_path=file_path)
                df = process_nans(df, column="Load")
                load[country] = df
    

    generated_data = []
    for country in generated.keys():
        df = pd.concat(generated[MAPPED_KEYS[country]], ignore_index=True)
        df['Country'] = MAPPED_KEYS[country]
        generated_data.append(df)
    generated_data = pd.concat(generated_data, ignore_index=True)

    for country in load.keys():
        load[country]['Country'] = MAPPED_KEYS[country]
    _load_data = pd.concat(load.values(), ignore_index=True)

    return generated_data, _load_data


def parse_arguments():
    parser = argparse.ArgumentParser(description='Data processing script for Energy Forecasting Hackathon')
    parser.add_argument(
        '--input_file',
        type=str,
        default='data/raw_data.csv',
        help='Path to the raw data file to process'
    )
    parser.add_argument(
        '--output_file', 
        type=str, 
        default='data/processed_data.csv', 
        help='Path to save the processed data'
    )
    parser.add_argument(
        '--folder_path', 
        type=str, 
        default='data/', 
        help='Path to save the processed data'
    )
    return parser.parse_args()





def main(input_file, output_file, data_folder, save_raw=True):
    generated, load = unify_data(data_path=data_folder)
    df = clean_data(generated, load, save_raw=save_raw)
    df = preprocess_data(df)
    if save_raw:
        save_data(df, output_file)

if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_file, args.output_file, data_folder=args.folder_path)