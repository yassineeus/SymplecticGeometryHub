# Automatic Update Configuration

## 📁 File Structure

Create this structure in your GitHub repository:

```
your-repo/
├── .github/
│   └── workflows/
│       └── update_symplectic_papers.yml
├── data/
│   ├── symplectic-papers.json
│   └── symplectic-papers-daily.json
├── index.html
├── articles-data.js
├── update_symplectic_papers.py
├── README.md
└── SETUP.md (this file)
```

## 🔧 Configuration Steps

### 1. Configure GitHub Actions Workflow

1. **Create the folder** `.github/workflows/` in your repository
2. **Copy** the `update_symplectic_papers.yml` file into it
3. **Modify** the environment variables in the file:
   ```yaml
   env:
     GITHUB_USER_NAME: your-username  # Replace with your GitHub username
     GITHUB_USER_EMAIL: your-email@example.com  # Replace with your email
   ```

### 2. Add the Python Script

1. **Copy** the `update_symplectic_papers.py` file to the root of your repo
2. **Make it executable** (optional):
   ```bash
   chmod +x update_symplectic_papers.py
   ```

### 3. Create Necessary Folders

```bash
mkdir data
touch data/symplectic-papers.json
touch data/symplectic-papers-daily.json
```

### 4. GitHub Permissions

Make sure your repository has permissions for:
- ✅ Actions (to run the workflow)
- ✅ Contents (to modify files)
- ✅ Metadata (to read repo info)

### 5. Manual Testing

You can test the script locally:

```bash
# Install dependencies
pip install arxiv requests pyyaml beautifulsoup4

# Run the script
python update_symplectic_papers.py
```

## ⚙️ Advanced Configuration

### Modify Update Frequency

In `update_symplectic_papers.yml`, change the line:
```yaml
- cron: "0 8 * * 1"  # Monday at 8:00 AM
```

**Examples:**
- `"0 8 * * *"` - Every day at 8:00 AM
- `"0 8 * * 1,4"` - Monday and Thursday at 8:00 AM
- `"0 8,20 * * *"` - Every day at 8:00 AM and 8:00 PM

### Modify Search Keywords

In `update_symplectic_papers.py`, modify the `self.keywords` list:
```python
self.keywords = [
    "symplectic geometry",
    "your-custom-keyword",
    # ... other keywords
]
```

### Change Number of Papers Retrieved

Modify the line in `run_update()`:
```python
all_papers = self.search_papers(max_results=200)  # Change 200
```

## 🚀 Activation

### Automatic Activation
The workflow will trigger automatically every Monday at 8:00 AM UTC.

### Manual Activation
1. Go to GitHub → your repository
2. Click on the **Actions** tab
3. Select **Update Symplectic Geometry Papers Weekly**
4. Click **Run workflow**

## 📊 Verification

After the first execution, you should see:

1. **New generated files:**
   - `articles-data.js` (updated)
   - `data/symplectic-papers.json`
   - `data/symplectic-papers-daily.json`
   - `README.md` (updated)

2. **Automatic commit** with the message:
   `🔄 Automatic update of symplectic geometry papers`

3. **Optional release** (if enabled) with statistics

## 🐛 Troubleshooting

### Workflow doesn't trigger
- Check that the file is in `.github/workflows/`
- Verify YAML syntax
- GitHub Actions permissions are enabled

### Permission errors
- Check repository permissions
- `GITHUB_TOKEN` is automatic

### No papers found
- Check connectivity to arXiv
- Keywords might be too restrictive
- Increase `max_results`

### Python script errors
- Check dependencies in `requirements.txt`
- Look at logs in Actions → your workflow

## 📝 Logs and Monitoring

- **GitHub Actions**: Detailed logs in the Actions tab
- **Python Script**: Debug messages in console
- **Generated Files**: Timestamps in JSON files

## 🔄 Maintenance

### Update Dependencies
Modify the section in the workflow:
```yaml
- name: Install Python Dependencies
  run: |
    python -m pip install --upgrade pip
    pip install arxiv==1.4.8  # Specify versions
    pip install requests==2.31.0
```

### Data Backup
JSON files in `data/` keep history. You can:
- Back them up periodically
- Archive them in releases
- Export to a database

## 🎯 Expected Result

After configuration, your site will:
- ✅ Update automatically every week
- ✅ Fetch latest symplectic geometry papers
- ✅ Generate necessary files for the website
- ✅ Automatically commit changes
- ✅ Work without manual intervention

## 📋 Quick Start Checklist

- [ ] Create `.github/workflows/` folder
- [ ] Add `update_symplectic_papers.yml` workflow file
- [ ] Update your username/email in the workflow
- [ ] Add `update_symplectic_papers.py` script
- [ ] Create `data/` folder
- [ ] Enable GitHub Actions in repository settings
- [ ] Test run the workflow manually
- [ ] Verify generated files are created
- [ ] Check automatic commits work

## 🔧 Customization Options

### Research Categories
Modify in the Python script:
```python
self.categories = [
    "math.SG",  # Symplectic Geometry
    "math.DG",  # Differential Geometry
    "math.AG",  # Algebraic Geometry
    "math-ph",  # Mathematical Physics
    "hep-th"    # High Energy Physics - Theory
]
```

### Output Format
Customize the `save_articles_data_js()` method to change the JavaScript output format.

### Filtering Logic
Adjust the `filter_symplectic_papers()` method to change relevance scoring.

## 🎨 Website Integration

The generated `articles-data.js` file will automatically work with your existing website search functionality. The format is:

```javascript
const articlesData = [
    {
        date: "2025-05-15",
        authors: "Author Names",
        title: "Paper Title",
        pdf: '<a href="arxiv-url">PDF</a>'
    },
    // ... more articles
];
```

This matches the expected format for your search interface!
