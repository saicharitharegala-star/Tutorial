# Flask Tutorial — Git & GitHub Assignment

A Flask frontend and MongoDB-backed API developed through a branching, merging, soft-reset, and rebase workflow.

## Repository and project origin

- Assignment repository: https://github.com/saicharitharegala-star/Tutorial
- Original project: `Flask_tutorial/` in `saicharitharegala-star/Devops_learnings`.
- Local working clone used for the assignment: `~/Tutorial_clean`.

The existing Flask source was copied into the separate `Tutorial` repository rather than rebuilt from scratch. The original `Flask_tutorial/` directory prefix was removed, leaving `backend/` and `frontend/` at the repository root. The original tutorial Word document was not part of the seven-file source copy.

## Project structure

```text
Tutorial/
├── backend/
│   ├── app.py
│   ├── data.json
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       ├── index.html
│       ├── success.html
│       └── todo.html
└── README.md
```

## What changed

| File | Work performed |
| --- | --- |
| `backend/data.json` | Replaced the original empty JSON list with student/API data on the `_new` branch. The data remains a JSON list, as expected by the existing API code. |
| `backend/app.py` | Retained the existing MongoDB helper and `/submit`, `/view`, and `/api` routes; added `POST /submittodoitem` to validate and store `itemName` and `itemDescription`. |
| `frontend/app.py` | Retained the original frontend behavior; added `GET /todo` to render the To-Do template and a frontend `POST /submittodoitem` handler to forward form data to the backend. |
| `frontend/templates/todo.html` | Added the Item Name and Item Description form, then added Item ID, Item UUID, and Item Hash in separate commits. Repaired the template after rich-text editing replaced its form controls with formatting-only HTML. |
| Other original source files | Copied as the starting project. No intentional assignment-specific changes to `index.html` or `success.html` were documented. |

The extra Item ID, UUID, and Hash inputs are form fields. The implementation described here does not automatically generate their values or persist them to MongoDB. The backend returns its own MongoDB document identifier as `itemId`; this is not the manually entered Item ID field.

## Branch workflow

### Task 1: Import the existing project

The `saicharitharegala-star` branch received the existing seven source files in commit `2fb8928` (`Add existing Flask tutorial project files`). Its merge into `main` appears as commit `57d611d`.

### Task 2: Update the JSON API data

The `saicharitharegala-star_new` branch updated `backend/data.json` in commit `f036108`. It was merged into `main` using:

```bash
git merge --no-ff origin/saicharitharegala-star_new -m "Merge updated API JSON into main"
git push origin main
```

The resulting merge commit was `f4355bf`. The supplied terminal evidence showed a successful push. This merge completed without a conflict; no conflict resolution was needed for that merge.

### Task 3: Develop frontend and backend separately

Both feature branches originated from `main`:

- `master_1`: To-Do frontend and submission forwarding; feature commit `7fa28b2`.
- `master_2`: MongoDB-backed `/submittodoitem` API; feature commit `bf26a18`.

Their merges into `main` appeared as `b7d8717` and `79a108a` respectively.

### Task 4: Separate field commits, soft reset, and rebase

The form fields were committed separately on `master_1`:

| Field | Original commit | After rebase |
| --- | --- | --- |
| Item ID | `a9875a8` | `a9875a8` |
| Item UUID | `a23a43d` | `b57c454` |
| Item Hash | `a28441e` | `92e7695` |

The branch was initially merged into `main` as `4f9081f`. A local backup branch named `backup-task4-before-reset` preserved that merge.

The subsequent workflow was:

```bash
git reset --soft a9875a8
git status
git --no-pager diff --cached -- frontend/templates/todo.html

git stash push -m "Task 4 UUID and Hash preserved after soft reset" -- frontend/templates/todo.html
git commit --allow-empty -m "Record Item ID-only state after soft reset"

git rebase main master_1
git checkout main
git merge --ff-only master_1
```

A soft reset moves the branch pointer but leaves the index and working files unchanged. Therefore, it initially retained the UUID and Hash changes staged. Those changes were saved in a stash to expose the actual ID-only version of the form. An intentionally empty checkpoint commit, `f2698b3`, recorded that state. Rebasing then replayed the UUID and Hash changes as separate commits without squashing.

This was an explicit interpretation of the assignment's ambiguous reset/recommit wording. It was not a claim that soft reset alone removed the later fields. Do not rerun these historical commands on an already completed project.

The last supplied local history showed `main` and `master_1` at `92e7695`, with a clean working tree. Final publishing commands were provided afterward:

```bash
git push origin main
git push --force-with-lease origin master_1
```

Their final successful outputs were not supplied for this README. Verify the live repository before claiming final synchronization. The lease-protected push is relevant only when updating the previously published, rebased `master_1`; it is not a routine command for every future push.

## Application architecture

```text
Browser → Frontend Flask app (port 8000)
        → Backend Flask API (port 9000)
        → MongoDB
```

The browser submits the To-Do form to the frontend. The frontend sends the name and description to the backend using `requests.post()`. The backend validates the values, inserts a document through the existing MongoDB collection helper, and returns HTTP 201 on success. The frontend redirects successful submissions to the existing success page.

### Relevant endpoints

| Service | Method | Route | Purpose |
| --- | --- | --- | --- |
| Frontend | GET | `/` | Existing home page |
| Frontend | GET | `/todo` | To-Do form |
| Frontend | POST | `/submittodoitem` | Forward To-Do form values to the backend |
| Frontend | GET | `/success` | Confirmation page |
| Frontend | GET | `/api` | Read the shared backend JSON file |
| Frontend | GET | `/get_data` | Proxy the backend's stored-record response |
| Backend | POST | `/submittodoitem` | Validate and store a To-Do item |
| Backend | GET | `/view` | Retrieve stored records, excluding `_id` |
| Backend | GET | `/api` | Return `backend/data.json` |
| Backend | POST | `/submit` | Existing generic form submission route |

## Local setup

Run commands from your own clone. The commands below assume the assignment's existing `Tutorial_clean` folder.

### 1. Create a Python environment and install dependencies

```bash
cd ~/Tutorial_clean
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt -r frontend/requirements.txt
python -m pip install certifi
```

The backend imports `certifi`, but its original requirements file did not explicitly list it. Ensure `backend/requirements.txt` includes `certifi` for reproducible installation, in addition to `flask`, `pymongo`, `dnspython`, and `python-dotenv`. The frontend needs `flask` and `requests`.

### 2. Configure MongoDB locally

Create `backend/.env` and supply your actual connection string:

```dotenv
MONGO_URI=replace_with_your_mongodb_connection_string
```

The existing helper connects to database `test`, collection `flask_tutorial`. The MongoDB service must be reachable and the credentials/network configuration must permit access.

Never commit `.env`, database credentials, or SSH private keys. Configure `.gitignore` or a local Git exclude rule before staging files. A sanitized `.env.example` may contain placeholders only.

The frontend defaults to `http://127.0.0.1:9000` for the backend; its `BACKEND_URL` environment variable can override this value.

### 3. Start the backend

```bash
cd ~/Tutorial_clean
source .venv/bin/activate
cd backend
python app.py
```

### 4. Start the frontend in another terminal

```bash
cd ~/Tutorial_clean
source .venv/bin/activate
cd frontend
python app.py
```

Open `http://127.0.0.1:8000/todo`. Do not open the HTML template directly from Finder: the template must be rendered through Flask/Jinja.

The supplied applications run in debug mode for coursework development. Do not expose them as a production service in that configuration.

## Verification

### Test the backend

```bash
curl -i -X POST http://127.0.0.1:9000/submittodoitem \
  --data-urlencode "itemName=Complete Git assignment" \
  --data-urlencode "itemDescription=Test MongoDB storage"

curl http://127.0.0.1:9000/view
curl http://127.0.0.1:9000/api
```

A successful submission is expected to return HTTP 201 with a success message and a MongoDB document ID. Missing name or description should produce HTTP 400. A database configuration/connection failure should produce HTTP 503.

### Check the frontend

- All five fields appear on `/todo`.
- No literal Jinja markers such as `{{ ... }}` or `{% ... %}` appear.
- Submitting the required name and description reaches the success page.
- The saved item is visible through the backend `/view` route.

End-to-end test screenshots were requested during the workflow but were not supplied for verification in this README. Treat these checks as acceptance criteria, not as a claim of verified test results.

### Check Git state

```bash
git fetch origin
git status
git rev-parse main origin/main master_1 origin/master_1
git log --oneline --graph --decorate -10
```

Immediately after publishing the final rebased result, all four refs should agree unless subsequent commits have been made. Do not apply the saved Task 4 stash to the final version: the UUID and Hash changes are already present after the rebase.

## Troubleshooting encountered

### Wrong repository root

The original local `Tutorial` folder was inside a home-directory repository whose remote pointed to `Python_learnings`, and an unrelated interactive rebase was pending. This caused confusing README conflicts and personal folders to appear in Git status.

The assignment continued in a separate SSH clone, `Tutorial_clean`, without deleting or altering the home-directory repository metadata. The earlier unrelated rebase was not confirmed as resolved. Before operating on any clone, verify:

```bash
pwd
git rev-parse --show-toplevel
git remote -v
```

### Template overwritten by rich-text editing

A screenshot showed `Cocoa HTML Writer` output and missing form controls. The template was rewritten as plain HTML/Jinja and subsequent edits were made using a source editor or `nano` rather than saving a rendered document through TextEdit.

### Git pager

Press `q` to exit the pager used by `git diff` or `git log`. For direct output:

```bash
git --no-pager diff -- frontend/templates/todo.html
```

## Security and scope limitations

This is a coursework demonstration, not a production authentication system. The original generic submission route stores submitted form values as supplied; do not use real passwords or sensitive personal information in tests. The To-Do implementation focuses on the assignment's required name/description storage. Add production security, validation, access control, and deployment configuration before any public use.

## Assignment submission

Package the complete project source with `Assignment_Documentation.docx`, genuine screenshots, explanations, and the repository link in one folder named `Git_and_GitHub_YourName`. Compress it to `Git_and_GitHub_YourName.zip` and submit the zip only. Exclude secrets, virtual environments, and generated caches. Finish replacing screenshot placeholders and verify the final pushes and application tests before submission.

## Documentation basis

This README reflects the assignment document, the existing source inspected during the conversation, and the student's supplied terminal evidence. Commit hashes describe the recorded workflow, not a fresh inspection of the current live GitHub repository.
