# modules/visualization.py

import matplotlib.pyplot as plt

def generate_personal_chat_plots(analysis_results, plot_filename_template, config):
    """Generate communication dynamics plots per year for personal chats."""
    daily_user_messages = analysis_results['daily_user_messages']
    daily_first_sender = analysis_results['daily_first_sender']

    all_dates = sorted(daily_user_messages.keys())
    years = sorted(set(date.year for date in all_dates))

    participants = list(analysis_results['user_counts'].keys())
    if len(participants) != 2:
        # Handle unexpected number of participants
        return
    user1, user2 = participants

    for year in years:
        dates = [date for date in all_dates if date.year == year]
        user1_counts = [daily_user_messages[date].get(user1, 0) for date in dates]
        user2_counts = [daily_user_messages[date].get(user2, 0) for date in dates]

        # Prepare the plot
        plt.figure(figsize=(12, 6))
        plt.plot(dates, user1_counts, label=user1, marker='o')
        plt.plot(dates, user2_counts, label=user2, marker='o')

        # Indicate the first sender of each day
        first_sender_marks = []
        sender_colors = []
        max_count = max(user1_counts + user2_counts) if (user1_counts + user2_counts) else 1
        for date in dates:
            if daily_first_sender[date] == user1:
                first_sender_marks.append(max_count * 1.05)
                sender_colors.append('blue')
            else:
                first_sender_marks.append(max_count * 1.05)
                sender_colors.append('orange')
        plt.scatter(dates, first_sender_marks, color=sender_colors, marker='^', s=50, zorder=5)

        plt.xlabel('Дата')
        plt.ylabel('Количество сообщений')
        plt.title(f'Активность общения в {year} году')
        plt.legend()
        plt.tight_layout()
        # Save the plot with the year in the filename
        plot_filename = plot_filename_template.replace('<year>', str(year))
        plt.savefig(plot_filename)
        plt.close()