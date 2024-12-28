import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import gradio as gr
import os

# Function to process work log and return average times, plots, and stats
def process_work_log(file_path, user):
    if user == "애리":
        empty_plot = plt.figure()
        stats_text = (
        f"2024년,{user}님은 출근기록이 없어요.  \n2025년 2월에 다시 만나요!"
        )
        return empty_plot, empty_plot, stats_text

    df = pd.read_csv(file_path)
    # Parse time and filter out invalid entries
    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')
    valid_df = df[(df['time'] < datetime.strptime('23:55:00', '%H:%M:%S'))]

    # Adjust times based on 'excuse' column for valid_df
    valid_df.loc[valid_df['excuse'] == '운동', 'time'] -= pd.to_timedelta(30, unit='minutes')
    valid_df = valid_df[valid_df['excuse'] != '연차']

    # Add weekday for analysis in valid_df
    valid_df['weekday'] = pd.to_datetime(valid_df[['year', 'month', 'day']]).dt.day_name()

    # Calculate average time by month in valid_df
    valid_df['entry_time_minutes'] = valid_df['time'].dt.hour * 60 + valid_df['time'].dt.minute
    monthly_avg = valid_df.groupby('month')['entry_time_minutes'].mean()

    # Convert minutes back to time format in valid_df
    monthly_avg_time = monthly_avg.dropna().apply(lambda x: timedelta(minutes=x))

    # Calculate average time by weekday in valid_df
    weekday_avg = valid_df.groupby('weekday')['entry_time_minutes'].mean().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )

    weekday_avg_time = weekday_avg.dropna().apply(lambda x: timedelta(minutes=x))

    # Mapping English weekdays to Korean
    weekday_korean = {
        'Monday': '월요일',
        'Tuesday': '화요일',
        'Wednesday': '수요일',
        'Thursday': '목요일',
        'Friday': '금요일',
        'Saturday': '토요일',
        'Sunday': '일요일'
    }

    # Identify trends in valid_df
    latest_month = monthly_avg.idxmax()
    earliest_month = monthly_avg.idxmin()
    latest_weekday = weekday_korean[weekday_avg.idxmax()]
    earliest_weekday = weekday_korean[weekday_avg.idxmin()]

    # Calculate total fine using full df
    total_score = df['score'].sum()
    total_fine = total_score * -100

    # Generate plots for valid_df
    monthly_plot = plt.figure(figsize=(10, 5))
    plt.bar(monthly_avg_time.index, monthly_avg_time.apply(lambda x: x.total_seconds() / 3600))
    plt.ylim(8, None)
    plt.xlabel('Month')
    plt.ylabel('Average Entry Time (Hours)')
    plt.title('Average Entry Time by Month')
    monthly_plot_fig = monthly_plot

    weekday_plot = plt.figure(figsize=(10, 5))
    plt.bar(weekday_avg_time.index, weekday_avg_time.apply(lambda x: x.total_seconds() / 3600))
    plt.ylim(8, None)
    plt.xlabel('Weekday')
    plt.ylabel('Average Entry Time (Hours)')
    plt.title('Average Entry Time by Weekday')
    weekday_plot_fig = weekday_plot

    stats_text = (
        f"2024년,{user}님은 평균적으로 {earliest_month}월에 일찍 출근 하셨고, {latest_month}월에 늦게 출근 하셨어요.  \n"
        f"요일 별로는 {earliest_weekday}에 일찍 출근 하는 편이었고, {latest_weekday}에 늦게 출근 하는 편이셨네요!  \n"
        f"총 {total_fine}원을 올해 납부하셨어요.😉"
    )

    return monthly_plot_fig, weekday_plot_fig, stats_text

# Gradio interface setup
def display_user_data(user):
    file_path = f'{user}.csv'
    monthly_plot, weekday_plot, stats_text = process_work_log(file_path,user)
    return stats_text, monthly_plot, weekday_plot
