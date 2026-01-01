# CoWrite (web application)
### Video Demo: https://youtu.be/A5_jkJxNF3I
### Description: 
CoWrite is my CS50 Final Project, and it's a web application where multiple writers collaboratively build a single piece of writing.

<img width="1658" height="898" alt="CoWrite Homepage" src="https://github.com/user-attachments/assets/1f53430c-eeae-4cb0-87de-2bbcc9818fca" />


## About CoWrite

### What is CoWrite?
CoWrite is a shared writing space where multiple writers collaborate on a single piece of writing. One user starts a story or text, and other users can progressively continue it by adding their own contributions. Each contribution builds on the existing text, allowing the piece to grow organically through collective creativity.

### What problem is CoWrite tackling?
As a writer, I have often found writing to be a solitary activity. While this can be productive, it can also feel isolating and limiting. CoWrite addresses this by turning writing into a collaborative process, bringing together different voices, ideas, and styles within a single work. This collaborative approach will often lead to unexpected twists and directions, even for the original author, making the writing process more dynamic and engaging.

### What pages does it have?
- **Homepage** (`index.html`): A simple landing page introducing the website and providing access to create a new draft.
- **How it works** (`how_it_works.html`): Explains the purpose of CoWrite and how users can interact with the platform.
- **My CoWriting** (requires login): A personal area where users can manage their drafts.
    - **New CoDraft** (`new_codraft.html`): Allows users to create a brand new collaborative draft.
    - **My CoDrafts** (`my_codrafts.html`): Displays drafts the user has created and drafts they have contributed to.
- **Community** (`community.html`): Shows all CoDrafts published by any user on the platform.
- **Profile** (`profile.html`): Displays a user’s profile information. Users can edit their own profile, while other profiles can be viewed without logging in.
- **Register** (`register.html`), **Login** (`login.html`), and **Logout** (`logout.html`): Authentication-related pages, available depending on the user’s login status.

There are additional pages, such as individual draft detail pages and the page for adding contributions, which are accessed contextually throughout the website rather than from the main navigation menu.

### Terminology
The name **CoWrite** comes from the combination of **Co**llaborative **Writing**. Throughout the website, this naming convention is extended using the **Co-** prefix, such as **CoDrafts**, to reinforce the collaborative nature of the platform.

### How can you use CoWrite?
Pages that provide general information, allow browsing drafts, and viewing user profiles are accessible without an account. However, creating drafts, contributing to existing drafts, and editing profiles require the user to be logged in.

To create a new work, a user can access the **New CoDraft** page (`new_codraft.html`) either from the homepage or from the *My CoDrafts* section. The creation form includes the following fields:

1. **Title**: The title of the piece. This cannot be edited after the draft is published.
2. **Category**: Indicates the intended style or length of the work. Available categories are:
    - Poetry
    - Short fiction
    - Longform
3. **Maximum contribution**: Defines the maximum amount each contributor can add to the piece. This limit is enforced both on the frontend and backend and cannot be modified after publication.
4. **Text**: The initial text of the piece. This does not need to be a complete or polished section, but rather a starting point or prompt for further development.

---

## Backend

### Framework
The backend of CoWrite is built using **Flask**, a lightweight Python web framework taught during CS50.

### Creation and access of the database
SQLAlchemy is used to define, create, and interact with the database. Unlike previous CS50 problem sets that relied on raw SQLite queries, this project uses SQLAlchemy’s ORM to model relationships and manage database interactions more efficiently. All database models are defined in the `models.py` file.

### Database tables
- **User**: Stores user information such as username, hashed password, profile image, and introduction text.
- **CoDraft**: Stores metadata about each draft, including title, category, creator, contribution limits, and completion status. The actual text of the piece is not stored here.
- **Contribution**: Stores each contribution’s text snapshot, author, timestamp, and associated CoDraft. This design allows the full evolution of a piece to be tracked over time.

### Backend files and folders
- `app.py`: Acts as the main controller, handling routing, application logic, and interactions between the frontend and the database.
- `helpers.py`: Contains helper functions for counting words, sentences, lines, and paragraphs, which are used to enforce contribution limits.
- `requirements.txt`: Lists all Python packages required to run the project.

Additional folders include:
- `flask_session/`: Stores session data for logged-in users.
- `instance/`: Contains the SQLite database file (`cowrite.db`).

---

## Frontend

### Styling and colour scheme
The frontend design focuses on clarity and simplicity, with minimal use of images to keep attention on the text. After experimenting with different palettes, I chose a contrasting cold–warm colour scheme:

- **Vanilla** (`#eae2b7`): Page background
- **Orange** (`#f77f00`): Buttons, draft information sections, and contribution highlights
- **Red** (`#d62828`): Hover states for buttons and navigation elements
- **Navy blue** (`#003049`): Primary text colour across the website

### Frontend files and folders
All HTML pages are created using **Jinja templates**, extending from a shared base layout (`layout.html`).

- `static/`:
    - `css/`: Contains `styles.css`, which defines the visual layout and styling.
    - `favicon_io/`: Stores the website’s favicon.
    - `profile_pics/`: Contains the default profile image (`default.png`) and any uploaded user profile images.
- `templates/`: Stores all HTML templates, including `layout.html` and individual page templates.

---

## Final thoughts
Initially, I considered implementing additional features such as:
- Likes and comments on each piece
- Private drafts shared only with selected users
- A clearly visible list of contributors for each piece
- Advanced filters on the Community page (by likes, upload date, completion status, etc.)

However, due to time constraints and the intended scope of the project, these features were left for potential future versions.

Learning and implementing SQLAlchemy for the first time was the most challenging aspect of this project, but it ultimately provided a much cleaner and more flexible way to manage data relationships. Through this project, I significantly deepened my understanding of Flask, Jinja templates, backend validation, and full-stack application design.

Overall, I am satisfied with the outcome of CoWrite. It demonstrates collaborative writing as a concept and reflects the skills I have developed throughout CS50.
