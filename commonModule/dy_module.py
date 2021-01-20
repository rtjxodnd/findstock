from commonModule import db_module
from datetime import datetime

# 당일
NOW_DY = datetime.today().strftime("%Y%m%d")


def now_dt(shape="%Y%m%d%H%M%S"):
    return datetime.today().strftime(shape)


def now_dy(shape="%Y%m%d"):
    return datetime.today().strftime(shape)


def now_tm(shape="%H%M%S"):
    return datetime.today().strftime(shape)


class Day:
    def __init__(self):
        self.db_class = db_module.Database()

    def trade_dy_yn(self, dy=NOW_DY):
        sql = "SELECT tr_dy_yn from findstock.cm_day_info WHERE dy = %s" % dy
        row = self.db_class.execute_one(sql)
        if row['tr_dy_yn'] == 'Y':
            return True
        else:
            return False

    def cal_tr_dy(self, diff_days=0, dy=NOW_DY):
        if diff_days >= 0:
            sql = " select sub.dy from (" \
                  "select @ROWNUM := @ROWNUM+1 as ROWNUM, a.dy " \
                  "from findstock.cm_day_info a, (SELECT @ROWNUM := -1) TMP " \
                  "where tr_dy_yn = 'Y' and a.dy >= '%s' " \
                  "order by a.dy asc) sub where sub.ROWNUM = %d" % (dy, diff_days)
        else:
            sql = " select sub.dy from (" \
                  "select @ROWNUM := @ROWNUM+1 as ROWNUM, a.dy " \
                  "from findstock.cm_day_info a, (SELECT @ROWNUM := -1) TMP " \
                  "where tr_dy_yn = 'Y' and a.dy <= '%s' " \
                  "order by a.dy desc) sub where sub.ROWNUM = %d" % (dy, -diff_days)

        row = self.db_class.execute_one(sql)
        return row['dy']


if __name__ == '__main__':
    day_class = Day()
    print(day_class.trade_dy_yn())
