import pandas as pd
import numpy as np
from shift_table import ShiftTable
from staff import Staff
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', default=2019, type=int)
    parser.add_argument('--month', default=3, type=int)
    parser.add_argument('--conditions', default=None, type=str)
    args = parser.parse_args()
    member_df = pd.read_csv('./member.csv')
    members = member_df.values.tolist()
    staff_list = []
    staff_id_list = []
    for i, member in enumerate(members):
        staff = Staff(member[0], member[1], member[2], member[3])
        staff_list.append(staff)
        staff_id_list.append(staff.id)
    staff_dict = {k:v for k, v in zip(staff_id_list, staff_list)}
    year = args.year
    month = args.month
    shift_table = ShiftTable(year, month,staff_dict)
    shift_table.assign()
    dir_path = 'export'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    exported_path =  '{}/{}_{}_shift_table.csv'.format(dir_path, year, month)
    shift_table.export(exported_path)
    analysis_path = '{}/{}_{}_analysis_report.csv'.format(dir_path, year, month)
    shift_table.export_analysis(analysis_path)
    
