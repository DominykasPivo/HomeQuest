from .models import UserInput

#acts as a service layer to handle business logic and database interactions (business layer)

def save_user_input(text):
    """Save user input to the database."""
    return UserInput.objects.create(text=text)

def get_all_user_inputs():
    """Retrieve all user inputs."""
    return UserInput.objects.all()