import matplotlib.pyplot as plt
import pandas as pd

# Load the data

file_name = 'cleaned_philippines_tourism_data.csv'
df = pd.read_csv(file_name)

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Menu System
while True:
    print("\n" + "="*50)
    print("PHILIPPINE TOURISM SYSTEM ANALYTICS MENU")
    print("="*50)
    print("[1] Generate Chart 1: Bar Graph (Spending per Destination)")
    print("[2] Generate Chart 2: Line Graph (Tourist Trends over Months)")
    print("[3] Generate Chart 3: Pie Chart (Accommodation Market Share)")
    print("[4] Generate Chart 4: Histogram (Distribution of Group Sizes)")
    print("[5] Generate Chart 5: Scatter Plot (Stay Days vs Spending)")
    print("[6] Exit")
    print("="*50)
    
    choice = input("Enter selection code (1-6): ").strip()
    
        
    if choice == '1':
        print("\nGenerating Bar Graph...")
        plt.figure()
        # Group by destination and find the average spending
        bar_data = df.groupby('Destination')['AvgSpendingPHP'].mean().sort_values(ascending=False).head(14)
        plt.bar(bar_data.index, bar_data.values, color='blue')
        plt.title('Average Spending per Destination')
        plt.xlabel('Destinations')
        plt.ylabel('Spending (PHP)')
        plt.xticks(rotation=15)
        plt.show()
        
    elif choice == '2':
        print("\nGenerating Line Graph...")
        plt.figure()
        # Group by month and sum the visitors
        line_data = df.groupby('Month')['NumberOfVisitors'].sum().reindex(month_order).fillna(0)
        plt.plot(line_data.index, line_data.values, marker='o', color='orange')
        plt.title('Total Visitors Over Months')
        plt.xlabel('Months')
        plt.ylabel('Total Visitors')
        plt.xticks(rotation=30)
        plt.show()
        
    elif choice == '3':
        print("\nGenerating Pie Chart...")
        plt.figure()
        # Count total visitors per accommodation type
        pie_data = df.groupby('Accommodation')['NumberOfVisitors'].sum()
        plt.pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%')
        plt.title('Accommodation Market Share')
        plt.show()
        
    elif choice == '4':
        print("\nGenerating Histogram...")
        plt.figure()
        # Explicitly targets the column 'NumberOfVisitors' distributed across bins
        plt.hist(df['NumberOfVisitors'], bins=8, color='purple', edgecolor='black', alpha=0.8)
        plt.title('Distribution of Visitor Group Sizes')
        plt.xlabel('Visitor Group Size (NumberOfVisitors)')
        plt.ylabel('Frequency (Number of Bookings)')
        plt.show()
        
    elif choice == '5':
        print("\nGenerating Scatter Plot...")
        plt.figure()
        # Simple scatter correlation plot using stay days and average spending
        plt.scatter(df['AvgStayDays'], df['AvgSpendingPHP'], color='red', alpha=0.7)
        plt.title('Stay Days vs Average Spending')
        plt.xlabel('Average Stay Days')
        plt.ylabel('Average Spending (PHP)')
        plt.show()
        
    elif choice == '6':
        print("\nExiting...")
        break
        
    else:
        print("\nInvalid choice selection. Please select an option between 1 and 6.")