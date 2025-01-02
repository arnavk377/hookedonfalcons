import numpy as np
import pandas as pd
import re

def extract_yards_gained(row):
    """Returns the number of yards gained on a play"""
    match = re.search(r'for (\d+) yard', row['details'])
    return int(match.group(1)) if match else 0

def penalty(row, opposing_team):
    """
    Returns a Series with penalty related stats
    pen_value: 1 if penalty on Atlanta, 0 if no penalty, -1 if penalty on other team
    pen_offender: the player who committed the penalty, default is np.nan
    net_yards: the net yards from the penalty, default is the net yards from the play
        if penalty was accepted, net_yards will be negative if penalty on ATL, positive if penalty on other team
    """
    pen_value = 1 if 'PENALTY' in row['details'] and 'No Play' in row['details'] else 0
    pen_value *= 1 if 'on ATL-' in row['details'] else -1
    pen_offender = np.nan
    if pen_value == 1:
        pen_offender = re.search(r'on ATL-([^\s,]+),', row['details']).group(1)
    elif pen_value == -1:
        pen_offender = re.search(rf'on {opposing_team}-([^\s,]+),', row['details']).group(1)
    if pen_value != 0:
        if 'No Play' in row['details']:
            net_yards = re.search(r', (\d+) yards, enforced', row['details']).group(1)
            net_yards *= -1 if pen_value == 1 else 1
        else:
            pen_yards = re.search(r', (\d+) yards, enforced', row['details']).group(1)
            if pen_value == 1:
                if row['possession'] == 'O':
                    net_yards -= pen_yards
                else:
                    net_yards += pen_yards
            elif pen_value == -1:
                if row['possession'] == 'O':
                    net_yards += pen_yards
                else:
                    net_yards -= pen_yards                
    else:
        net_yards = row['net_yards']
    return pd.Series({'penalty': pen_value, 'pen_offender': pen_offender, 'net_yards': net_yards})

def turnover_sack(row):
    """
    Returns a Series with turnover and sack stats
    sack: 1 if sack, 0 if not
    turnover: 1 if turnover(fumble or interception), 0 if not
    """
    sack = 1 if 'sacked' in row['details'] else 0
    recovery = re.search(r'recovered by (\w+)-', row['details'])
    if recovery and 'no play' not in row['details']:
        if 'FUMBLES' in row['details'] and ((recovery.group(1) == 'ATL' and row['possession'] == 'D') or (recovery.group(1) != 'ATL' and row['possession'] == 'O')):
            turnover = 1
        else:
            turnover = 0
    else:
        if 'INTERCEPTED' in row['details']:
            turnover = 1
            row['net_yards'] = 0
        else:
            turnover = 0
    return pd.Series({'sack': sack, 'turnover': turnover})

def json_to_csv(json_file, csv_file, opposing_team):
    """Tidies and converts a json file to a csv file"""
    df = pd.read_json(json_file)
    # replaces all null/semi-null values with np.nan
    for i in df.columns:
        df[i].replace({'': np.nan, None: np.nan, 'None': np.nan}, inplace=True)
    # extracts the number of yards gained on a play
    df['net_yards'] = df.apply(extract_yards_gained, axis=1)
    # extracts penalty related stats
    df[['penalty', 'pen_offender', 'net_yards']] = df.apply(penalty, axis=1, args=(opposing_team,))
    # extracts turnover and sack stats
    df[['sack', 'turnover']] = df.apply(turnover_sack, axis=1)
    # drops columns to shorten length of csv file
    new_df = df.drop(columns=['details', 'description'], inplace=True)
    new_df.to_csv(csv_file)