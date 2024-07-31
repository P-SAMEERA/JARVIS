import webbrowser;
# Function to add two numbers
def add_numbers(num1, num2):
    return num1 + num2

# Get the two numbers from the user
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))

# Add the two numbers
sum = add_numbers(num1, num2)

# Print the result
webbrowser.open("youtube.com")
print("The sum of the two numbers is:", sum)