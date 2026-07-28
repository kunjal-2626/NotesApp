# 📝 Notes Management System

A simple and responsive Notes Management System developed using **Flask**. The application allows users to create, view, edit, and delete notes through a clean and user-friendly interface.

---

## 🚀 Features

- ➕ Add new notes
- 📖 View all saved notes
- ✏️ Edit existing notes
- 🗑️ Delete notes
- 🔍 Search notes (if implemented)
- 📱 Responsive user interface
- 💾 Persistent data storage using a database

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend:** Flask (Python)
- **Database:** MySQL
- **Template Engine:** Jinja2

---

## 📂 Project Structure

```
NotesManagementSystem/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── add_note.html
│   ├── edit_note.html
│   └── ...
│
├── app.py
├── requirements.txt
├── README.md
└── database.sql
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/NotesManagementSystem.git
```

### Navigate to the project

```bash
cd NotesManagementSystem
```

### Create a virtual environment

**macOS/Linux**

```bash
python3 -m venv venv
```

**Windows**

```bash
python -m venv venv
```

### Activate the virtual environment

**macOS/Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

1. Create a MySQL database.

```sql
CREATE DATABASE notes_management;
```

2. Update your MySQL credentials in `app.py`.

```python
host="localhost"
user="root"
password="your_password"
database="notes_management"
```

3. Import the SQL file if provided.

---

## ▶️ Run the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

Add screenshots of the application here.

Example:

```
Home Page
Add Note
Edit Note
Dashboard
```

---

## 🎯 Future Enhancements

- User Authentication
- Categories and Tags
- Rich Text Editor
- Dark Mode
- Export Notes to PDF
- File Attachments
- Note Sharing
- Cloud Storage Integration

---

## 👨‍💻 Author

**Kunjal Sri Hari Priya**

- GitHub: https://github.com/YOUR_USERNAME
- LinkedIn: https://www.linkedin.com/in/kunjal-sri-hari-priya/

---

## 📄 License

This project is developed for learning and educational purposes.
