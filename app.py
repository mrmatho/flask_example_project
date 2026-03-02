from flask import Flask, render_template, request, redirect, url_for
from csv import DictReader, DictWriter
from datetime import date

app = Flask(__name__)

# Display the home page with all logged workouts.
@app.route('/')
def index():
    workouts = get_workouts_from_csv()
    return render_template('index.html', workouts = workouts)


# Display just one workout by its index in the CSV file. Redirect to home if the index is invalid.
@app.route('/view/<int:workout_id>')
def view_workout(workout_id):
    workouts = get_workouts_from_csv()

    if workout_id < 0 or workout_id >= len(workouts):
        return redirect(url_for('index'))

    return render_template(
        'view_workout.html',
        workout=workouts[workout_id],
        workout_id=workout_id
    )

# Read all workout rows from the CSV file.
def get_workouts_from_csv() -> list[dict]:
    workouts = []
    with open('workouts.csv', 'r') as file:
        reader = DictReader(file)
        for row in reader:
            row.setdefault('time', '')
            workouts.append(row)
    return workouts


# Overwrite the CSV file with the provided workout list.
def save_workouts_to_csv(workouts: list[dict]) -> None:
    with open('workouts.csv', 'w', newline='') as file:
        fieldnames = ['date', 'exercise', 'sets', 'reps', 'weight', 'time']
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(workouts)
    

# Show the add form on GET, and save a new workout on POST.
@app.route('/add', methods=['GET', 'POST'])
def add_workout():
    if request.method == 'POST':
        workouts = get_workouts_from_csv()
        workouts.append({
            'date': request.form['date'],
            'exercise': request.form['exercise'],
            'sets': request.form['sets'],
            'reps': request.form['reps'],
            'weight': request.form['weight'],
            'time': request.form.get('time', '').strip()
        })
        save_workouts_to_csv(workouts)

        return redirect(url_for('index'))
    
    return render_template('add_workout.html', default_date=date.today().isoformat())


# Show the edit form for one workout on GET, and save updates on POST.
@app.route('/edit/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    workouts = get_workouts_from_csv()

    if workout_id < 0 or workout_id >= len(workouts):
        return redirect(url_for('index'))

    if request.method == 'POST':
        workouts[workout_id] = {
            'date': request.form['date'],
            'exercise': request.form['exercise'],
            'sets': request.form['sets'],
            'reps': request.form['reps'],
            'weight': request.form['weight'],
            'time': request.form.get('time', '').strip()
        }
        save_workouts_to_csv(workouts)
        return redirect(url_for('index'))

    return render_template(
        'edit_workout.html',
        workout=workouts[workout_id],
        workout_id=workout_id
    )


# Delete a single workout by its index and save the updated list.
@app.route('/delete/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    workouts = get_workouts_from_csv()

    if workout_id < 0 or workout_id >= len(workouts):
        return redirect(url_for('index'))

    workouts.pop(workout_id)
    save_workouts_to_csv(workouts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)