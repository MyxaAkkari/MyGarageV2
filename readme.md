# My Garage App

My Garage is a simple Flask web application that allows users to manage a list of cars. Users can add new cars, mark them as fixed, delete cars, and edit car details.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Add Cars:** Users can add new cars to the garage by providing owner details, brand, model, model year, and color.

- **List Cars:** The home page displays a list of all cars in the garage, including their details.

- **Delete Cars:** Users can delete a car from the garage, which moves the car to the "Fixed Cars" section.

- **Fix Cars:** Deleted cars are moved to the "Fixed Cars" section for reference.

- **Edit Cars:** Users can edit the details of a car.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MyxaAkkari/MyGarageV2.git
2. Navigate to the project directory:
    ```bash
    cd MyGarageV2
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
4. Run the application:
    ```bash
    python app.py

## Usage

1. Access the application by visiting [http://localhost:8000/](http://localhost:8000/) in your web browser.
2. Add new cars using the input form on the home page.
3. Delete, fix, or edit existing cars using the respective buttons.

## Dependencies

- Flask
- SQLite3

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue.

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request.



```sql
Feel free to adjust any details or add specific information related to your project.
