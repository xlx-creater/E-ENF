from datetime import datetime
from get_str_date import get_month_str, get_week_str

# ################ find_reference_wav_filename
def date_wav_filename(ENF_Year, ENF_Month, ENF_date_Begin, ENF_date_End, ENF_Hour_Begin, ENF_Hour_End):
    # ################  Judgment of time
    begin_time_str = ENF_Year + '-' + ENF_Month + '-' + ENF_date_Begin
    end_time_str = ENF_Year + '-' + ENF_Month + '-' + ENF_date_End

    begin_week_int = datetime.strptime(begin_time_str, '%Y-%m-%d').weekday()
    end_week_int = datetime.strptime(end_time_str, '%Y-%m-%d').weekday()

    begin_week_str = get_week_str(begin_week_int)
    end_week_str = get_week_str(end_week_int)

    ENF_Year_int = int(ENF_Year)
    ENF_Month_int = int(ENF_Month)
    ENF_date_Begin_int = int(ENF_date_Begin)
    ENF_date_End_int = int(ENF_date_End)
    ENF_Hour_Begin_int = int(ENF_Hour_Begin)
    ENF_Hour_End_int = int(ENF_Hour_End)

    month_str = get_month_str(ENF_Month_int)

    # ######reference filename judgment
    # ##  within one day
    if ENF_date_Begin_int == ENF_date_End_int:
        Num_of_File = ENF_Hour_End_int - ENF_Hour_Begin_int
        storeFileStrings = ''
        if ENF_date_End_int < 10:
            ENF_date_str = '0' + str(ENF_date_End_int)
        else:
            ENF_date_str = str(ENF_date_End_int)
        for ii in range(Num_of_File):
            newHour = ENF_Hour_Begin_int + ii + 1
            newHour = '%02d' % newHour
            storeFileStrings = storeFileStrings + ENF_Year + '_' + month_str + '_' + ENF_date_str + '_' + end_week_str + '_'+ newHour + '_00_00'
    # ## within two days
    elif ENF_date_End_int - ENF_date_Begin_int == 1:
        Num_of_File = 23 - ENF_Hour_Begin_int + ENF_Hour_End_int + 1
        storeFileStrings = ''
        if ENF_date_Begin_int < 10:
            ENF_date_str_B = '0' + str(ENF_date_Begin_int)
        else:
            ENF_date_str_B = str(ENF_date_Begin_int)
        if ENF_date_End_int < 10:
            ENF_date_str_E = '0' + str(ENF_date_End_int)
        else:
            ENF_date_str_E = str(ENF_date_End_int)

        for ii in range(23 - ENF_Hour_Begin_int):
            newHour = str(ENF_Hour_Begin_int + ii + 1)
            newHour = '%02d' % int(newHour)
            storeFileStrings = storeFileStrings + ENF_Year + '_' + month_str + '_' + ENF_date_str_B + '_' + end_week_str + '_' + newHour + '_00_00'
        counterF = 0
        for ii in range(Num_of_File - 23 + ENF_Hour_Begin_int):
            newHour = str(counterF)
            newHour = '%02d' % int(newHour)
            storeFileStrings = storeFileStrings + ENF_Year + '_' + month_str + '_' + ENF_date_str_E + '_' + end_week_str + '_' + newHour + '_00_00'
            counterF = counterF + 1

    # ## within more than two days
    elif ENF_date_End_int - ENF_date_Begin_int > 1:
        Num_of_File = (ENF_date_End_int - ENF_date_Begin_int - 1) * 24 + 23 - ENF_Hour_Begin_int + ENF_Hour_End_int + 1
        Num_of_Full_Days = ENF_date_End_int - ENF_date_Begin_int - 1
        WeekDayStrings = ''
        for ii in range(Num_of_Full_Days + 2):
            NumOfDate = ENF_date_Begin_int + ii
            time_str = ENF_Year + '-' + ENF_Month + '-' + str(NumOfDate)
            week_int = datetime.strptime(time_str, '%Y-%m-%d').weekday()
            week_str = get_week_str(week_int)
            WeekDayStrings = WeekDayStrings + week_str

        FileStringA = ''
        FileStringB = ''
        FileStringC = ''
        if ENF_date_Begin_int < 10:
            ENF_date_str_B = '0' + str(ENF_date_Begin_int)
        else:
            ENF_date_str_B = str(ENF_date_Begin_int)
        if ENF_date_End_int < 10:
            ENF_date_str_E = '0' + str(ENF_date_End_int)
        else:
            ENF_date_str_E = str(ENF_date_End_int)

        # first day
        for ii in range(1, 24 - ENF_Hour_Begin_int):
            newHour = str(ENF_Hour_Begin_int + ii)
            newHour = '%02d' % int(newHour)
            FileStringA = FileStringA + ENF_Year + '_' + month_str + '_' + ENF_date_str_B + '_' + end_week_str + '_' + newHour + '_00_00'
        # last day
        counterF = 0
        for ii in range(1, ENF_Hour_End_int + 2):
            newHour = str(counterF)
            newHour = '%02d' % int(newHour)
            FileStringC = FileStringC + ENF_Year + '_' + month_str + '_' + ENF_date_str_E + '_' + end_week_str + '_' + newHour + '_00_00'
            counterF = counterF + 1

        # full days between
        for ii in range(1, Num_of_Full_Days + 1):
            newDate = str(ENF_date_Begin_int + ii)
            if int(newDate) < 10:
                newDate = '_' + newDate
            for jj in range(1, 25):
                newHour = str(jj - 1)
                newHour = '%02d' % int(newHour)
                FileStringB = FileStringB + ENF_Year + '_' + month_str + '_' + newDate  + '_' + WeekDayStrings[
                                            ii * 3:ii * 3 + 3] + '_' + newHour + '_00_00'
        storeFileStrings = FileStringA + FileStringB + FileStringC
    return storeFileStrings



    




