# README - Setting Up and Running the Project

This README provides instructions on how to set up a Python environment, install the required packages using `pip`, and run a Django project. Additionally, it includes some essential steps and recommendations for a smooth development experience.

## Prerequisites

Before you begin, ensure you have the following prerequisites installed on your system:

- Python (3.6 or higher): [Python Installation Guide](https://www.python.org/downloads/)

## Setup Environment

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/alwenpy/ETHNO.git
   cd ethno-ecommerce 
   ```

2. Create a virtual environment to isolate project dependencies. This step is highly recommended to avoid conflicts with system-wide packages:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

## Install Dependencies

1. Install `pip-tools` if not already installed. This tool helps manage dependencies efficiently:

   ```bash
   pip install pip-tools
   ```

2. To install project-specific dependencies from the `requirements.txt` file, run:

   ```bash
   pip-sync requirements.txt
   ```

   This command ensures that your virtual environment contains the required packages.


## Running the Django Project

1. Start the development server:

   ```bash
   python manage.py runserver
   ```

   The development server will run at `http://127.0.0.1:8000/` by default. You can access the Django admin interface at `http://127.0.0.1:8000/admin/` to manage your application's data.

2. Open your web browser and navigate to the server address to view your Django project.

## Additional Instructions

- **Static Files**: If your project uses static files (CSS, JavaScript, etc.), run `python manage.py collectstatic` to collect and store these files in a designated directory.

- **Superuser**: To create a superuser account for the Django admin interface, use the following command:

  ```bash
  python manage.py createsuperuser
  ```

- **Virtual Environment Deactivation**: To deactivate the virtual environment, simply run:

  ```bash
  deactivate
  ```

## Contributing

If you wish to contribute to this project, please follow the [Contributing Guidelines](CONTRIBUTING.md) in the repository.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license.

For more information and documentation about Django, please refer to the [Django Documentation](https://docs.djangoproject.com/).

