import datetime

def get_date() -> tuple[str]:
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - datetime.timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    
    init_date = first_day_last_month.strftime('%Y-%m-%d')
    end_date = last_day_last_month.strftime('%Y-%m-%d')

    return init_date, end_date
