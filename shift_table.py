import calendar
import const
from date import Date
import pandas as pd
import copy
import numpy as np

class ShiftTable(object):
    def __init__(self, year, month, staff_dict, path=None):
        self.year = year
        self.month = month
        first_monday, n_days = calendar.monthrange(self.year, self.month)
        first_day = calendar.weekday(self.year, self.month, 1)
        contents = []
        day = first_day
        for d in range(n_days):
            day = (day + d ) % 7
            contents.append(Date(day))
        self.contents = contents
        if(path == None):
            self.initialize()
        else:
            self.load_conditions(path)
        self.staff_dict = staff_dict
    
    def initialize(self):
        # 条件の初期化 load_conditions用のファイルがない場合はこっちを使用する．
        # 月曜日 早1と居3
        # 火曜日 早2-2，居2
        # 水曜日 早1, 居3
        # 木曜日 早2-2，居2
        # 金曜日 早1，居3
        # 土曜日 早1，早2-1,2-2, 居1, 居2
        # 日曜日 全日
        # 21日は 全日
        for date, date_obj in enumerate(self.contents):
            if date == 21:
                for job in date_obj.late_jobs.values():
                    job = False
                for job in date_obj.early_jobs.values():
                    job = False
            if date_obj.day == 0:
                date_obj.early_jobs['es1'] = False
                date_obj.late_jobs['ls3'] = False
            if date_obj.day == 1:
                date_obj.early_jobs['es3'] = False
                date_obj.late_jobs['ls2'] = False
            if date_obj.day == 2:
                date_obj.early_jobs['es1'] = False
                date_obj.late_jobs['ls3'] = False
            if date_obj.day == 3:
                date_obj.early_jobs['es3'] = False
                date_obj.late_jobs['ls2'] = False
            if date_obj.day == 4:
                date_obj.early_jobs['es1'] = False
                date_obj.late_jobs['ls3'] = False
            if date_obj.day == 5:
                date_obj.early_jobs['es2'] = False
                date_obj.early_jobs['es3'] = False
                date_obj.late_jobs['ls1'] = False
                date_obj.late_jobs['ls2'] = False
            if date_obj.day == 6:
                for job in date_obj.late_jobs.values():
                    job = False
                for job in date_obj.early_jobs.values():
                    job = False

    def load_conditions(self):
        # シフトテーブルの情報を読み込み
        conditions = pd.read_csv().tolist()
        for i, condition in enumerate(conditions):
            date = self.contents[i]
            for j, job in enumerate(condition):
                if job == '-':
                    if j < 3:
                        date.early_jobs[j] = False
                    else:
                        date.late_jobs[j] = False

    def _remove_matches(self, candidate_list, target_charge,):
        # target_chargeと同じchargeの先生は削除
        matches = [cand for cand in candidate_list if self.staff_dict[cand].get_charge() == target_charge]
        for match in matches:
            candidate_list.remove(match)
        return candidate_list

    def _remove_assigned_candidates(self, candidate_list, assigned_staff):
        for staff in assigned_staff:
            if type(staff) != bool and staff in candidate_list:
                candidate_list.remove(staff)
        return candidate_list

    def _show_name_order(self, id_list):
        name_list = [self.staff_dict[staff_id].name for staff_id in id_list]
        print(name_list)

    def _sort_by_total_works(self, candidate_list):
        total_num_list = []
        print(candidate_list)
        for candidate in candidate_list:
            total_num_list.append(self.staff_dict[candidate].get_total_works())
        dictionary = {k:v for k, v in zip(candidate_list, total_num_list)}
        return [can_id[0] for can_id in sorted(dictionary.items(), key=lambda x: x[1])]

    def _sort_by_late_works(self, candidate_list):
        late_num_list = []
        print(candidate_list)
        for candidate in candidate_list:
            late_num_list.append(self.staff_dict[candidate].get_n_late_works())
        dictionary = {k:v for k, v in zip(candidate_list, late_num_list)}
        return [can_id[0] for can_id in sorted(dictionary.items(), key=lambda x: x[1])]
    
    def _sort_by_early_works(self, candidate_list):
        early_num_list = []
        print(candidate_list)
        for candidate in candidate_list:
            early_num_list.append(self.staff_dict[candidate].get_n_early_works())
        dictionary = {k:v for k, v in zip(candidate_list, early_num_list)}
        return [can_id[0] for can_id in sorted(dictionary.items(), key=lambda x: x[1])]

    def assign(self):
        candidate_list = [staff.id for staff in list(self.staff_dict.values())]
        for i_date, date in enumerate(self.contents):
            # Sort by total number of assign
            assigned_list = []
            candidate_list = self._sort_by_total_works(candidate_list)
            # アサインされてる回数順にソート(Stable sort)
            print("{}/{}/{} {} total_sorted:".format(self.year, self.month, i_date, self.trans_day_str(date.day)))
            self._show_name_order(candidate_list)
            early_candidate_list = self._sort_by_early_works(candidate_list)
            print("{}/{}/{} {} early_sorted:".format(self.year, self.month, i_date, self.trans_day_str(date.day)))
            self._show_name_order(early_candidate_list)
            for key, job in date.early_jobs.items():
                # 早番
                if job:
                    assignee = early_candidate_list[0]
                    date.early_jobs[key] = self.staff_dict[assignee]
                    assigned_list.append(assignee)
                    self.staff_dict[assignee].early_work()
                    target_charge = self.staff_dict[assignee].get_charge()
                    # candidate_listの更新
                    early_candidate_list.remove(assignee)
                    self._remove_matches(early_candidate_list, target_charge)

                    # staffのassign
                    # 早番に同じchargeの人がいない
                    # 遅番に同じchargeの人がいない
                    # 最低一回は早番と遅番をしなければならない．
                    # 月でスタッフが同じだけのジョブをしなければならない

            late_candidate_list = copy.deepcopy(candidate_list)
            print("assigned_list: {}".format(assigned_list))
            self._remove_assigned_candidates(late_candidate_list, assigned_list)
            late_candidate_list = self._sort_by_late_works(late_candidate_list)
            print("{}/{}/{} {} late_sorted:".format(self.year, self.month, i_date, self.trans_day_str(date.day)))
            self._show_name_order(late_candidate_list)
            print("\n")
            for key, job in date.late_jobs.items():
                # 遅番
                if job:
                    assignee = late_candidate_list[0]
                    date.late_jobs[key] = self.staff_dict[assignee]
                    assigned_list.append(assignee)
                    self.staff_dict[assignee].late_work()
                    target_charge = self.staff_dict[assignee].get_charge()
                    # candidate_listの更新
                    late_candidate_list.remove(assignee)
                    self._remove_matches(late_candidate_list, target_charge)
        print("Assigned")

    def export(self, path):
        header = ["年", "月", "日", "曜日", "早1", "早2", "早2", "居1", "居2", "居3"]
        export_table = []
        for date, date_obj in enumerate(self.contents):
            row = [self.year, self.month, date, self.trans_day_str(date_obj.day), self.trans_export_format(date_obj.early_jobs['es1']), self.trans_export_format(date_obj.early_jobs['es2']), self.trans_export_format(date_obj.early_jobs['es3']), self.trans_export_format(date_obj.late_jobs['ls1']), self.trans_export_format(date_obj.late_jobs['ls2']), self.trans_export_format(date_obj.late_jobs['ls3'])]
            export_table.append(row)
        export_df = pd.DataFrame(export_table, columns=header)
        export_df.to_csv(path)
        print("Exported to {}".format(path))

    def export_analysis(self, path):
        header = ["id", "名前", "担当年齢", "早番回数", "遅番回数", "合計回数"]
        export_table = []
        for staff in self.staff_dict.values():
            export_table.append(staff.export())
        export_df = pd.DataFrame(export_table, columns=header)
        export_df.to_csv(path)
        print("Exported to {}".format(path))
    
    def trans_export_format(self, staff):
        if staff:
            return staff.name_kanji
        else:
            return '-'

    def trans_day_str(self, day):
        if day==0:
            return '月'
        if day==1:
            return '火'
        if day==2:
            return '水'
        if day==3:
            return '木'
        if day==4:
            return '金'
        if day==5:
            return '土'
        if day==6:
            return '日'