 ######### Judging the month
def get_month_str(E_month):
    month_str = {
        1 : '01',
        2 : '02',
        3 : '03',
        4 : '04',
        5 : '05',
        6 : '06',
        7 : '07',
        8 : '08',
        9 : '09',
        10: '10',
        11: '11',
        12: '12'
        }
    return month_str[E_month]


######### Judging the week
def get_week_str(E_week):
    week_str={
        0: 'Mon',
        1: 'Tue',
        2: 'Wed',
        3: 'Thu',
        4: 'Fri',
        5: 'Sat',
        6: 'Sun',
        }
    return week_str[E_week]
