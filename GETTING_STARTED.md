# Getting Started — Step-by-Step Setup Guide

This guide assumes you're starting from scratch on a Mac, Windows, or Linux machine.

---

## Step 1: Install Python (if you don't have it)

### Mac
Open the **Terminal** app (search for "Terminal" in Spotlight), then run:
```bash
# Install Homebrew (a package manager) if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

### Windows
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. **IMPORTANT**: During install, check the box that says **"Add Python to PATH"**
4. Click "Install Now"
5. Open **Command Prompt** (search for "cmd" in the Start menu)

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3-pip git
```

### Verify Python is installed
```bash
python3 --version
```
You should see something like `Python 3.11.x` or higher.

---

## Step 2: Install Git (if you don't have it)

### Mac
```bash
brew install git
```

### Windows
1. Go to https://git-scm.com/download/win
2. Download and install (use all default options)
3. Close and reopen Command Prompt after installing

### Verify Git is installed
```bash
git --version
```

---

## Step 3: Download (clone) this project

Open your terminal and run these commands one at a time:

```bash
# Go to your home directory (or wherever you want to put the project)
cd ~

# Download the project from GitHub
git clone https://github.com/awaiken/hello-world.git

# Go into the project folder
cd hello-world

# Switch to the branch with the AI training code
git checkout claude/ai-training-content-agent-ddHx2
```

---

## Step 4: Install the project and its dependencies

```bash
# This installs the project and all the libraries it needs
pip install -e .
```

If `pip` doesn't work, try `pip3` instead:
```bash
pip3 install -e .
```

Wait for it to finish. You'll see "Successfully installed..." when it's done.

---

## Step 5: (Optional) Set up API keys for better results

The tool works **without any API keys** — it will search arXiv and GitHub by default.
But for the best results, you can add API keys.

```bash
# Create your config file from the template
cp .env.example .env
```

Then open the `.env` file in any text editor and fill in the values:

### How to get a GitHub token (free, recommended)
1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name like "ai-catalog"
4. Check the box for **"public_repo"** (that's all you need)
5. Click "Generate token"
6. Copy the token and paste it into your `.env` file:
   ```
   ATC_GITHUB_TOKEN=ghp_your_token_here
   ```

### How to get Google Custom Search keys (optional, free tier)
1. Go to https://programmablesearchengine.google.com/
2. Click "Add" to create a new search engine
3. Under "What to search", select "Search the entire web"
4. Give it a name and click "Create"
5. Copy the **Search Engine ID** — paste it as `ATC_GOOGLE_CSE_ID` in `.env`
6. Go to https://console.cloud.google.com/apis/credentials
7. Create a new API key — paste it as `ATC_GOOGLE_API_KEY` in `.env`

---

## Step 6: Run the discovery agent

This is the command that searches the internet for free AI training content:

```bash
# Search for resources across all AI skill domains
ai-catalog discover
```

Or search specific topics only:
```bash
# Just machine learning basics and deep learning
ai-catalog discover --domains ml_basics,deep_learning

# Just business skills
ai-catalog discover --domains ai_strategy,ai_ethics,ai_roi
```

**What you'll see:** The tool prints a report showing how many resources it found
and added to the catalog. Example output:
```
============================================================
Discovery Report
============================================================
  Queries executed:     312
  Unique results found: 87
  New resources added:  45
  Resources updated:    12
  Below threshold:      30
  Total in catalog:     45
============================================================
```

---

## Step 7: Ingest and analyse the content

This step scrapes the discovered websites, removes duplicates, and categorises everything:

```bash
ai-catalog ingest
```

**What you'll see:**
```
============================================================
Ingestion Report
============================================================
  Resources processed:  45
  Successfully scraped: 38
  Failed:               7
  Duplicate groups:     3
  Duplicates flagged:   5
  Recategorised:        33
============================================================
```

---

## Step 8: Generate the curriculum

This creates a structured training programme from all the content:

```bash
# Generate and save to a file
ai-catalog generate --output curriculum.json
```

**What you'll see:**
```
============================================================
Curriculum Generation Report
============================================================
  Title:            Comprehensive AI Best Practices Curriculum
  Learning paths:   12
  Total hours:      85.3
  Domains covered:  ['ml_basics', 'deep_learning', 'nlp', ...]

  [     beginner] Ml Basics — Beginner
                   3 modules, 18.5h
  [intermediate] Ml Basics — Intermediate
                   2 modules, 12.0h
  ...

  Validation: 0 errors, 4 warnings
============================================================
```

The full curriculum is saved in `curriculum.json` — open it with any text editor.

---

## Step 9: Explore your catalog

```bash
# See statistics about what was found
ai-catalog catalog stats

# List the top resources
ai-catalog catalog list

# List only NLP resources with high quality scores
ai-catalog catalog list --domain nlp --min-score 0.5

# Export everything to a file
ai-catalog catalog export --output my_catalog.json
```

---

## Available Skill Domains

Use these exact names with the `--domains` flag:

| Domain Name | Description |
|---|---|
| `ml_basics` | Machine Learning Fundamentals |
| `deep_learning` | Deep Learning (neural networks, CNNs, etc.) |
| `nlp` | Natural Language Processing |
| `computer_vision` | Computer Vision |
| `mlops` | MLOps & Production ML |
| `generative_ai` | Generative AI (LLMs, diffusion models) |
| `reinforcement_learning` | Reinforcement Learning |
| `data_engineering` | Data Engineering for AI |
| `ai_strategy` | AI Strategy |
| `ai_ethics` | AI Ethics & Responsible AI |
| `ai_project_management` | AI Project Management |
| `ai_roi` | AI Return on Investment |
| `ai_governance` | AI Governance & Compliance |

Combine multiple with commas: `--domains ml_basics,deep_learning,nlp`

---

## Troubleshooting

### "command not found: ai-catalog"
Try running it with Python directly:
```bash
python -m ai_training_catalog.cli discover
```
Or if you're on Windows:
```bash
python3 -m ai_training_catalog.cli discover
```

### "pip: command not found"
Use `pip3` instead of `pip` in all commands.

### "Permission denied" errors
Add `--user` to the pip install:
```bash
pip install --user -e .
```

### Very few results found
- Add a GitHub token (see Step 5) — this significantly increases results
- Add Google API keys for web-wide search
- Try running discovery multiple times; results may vary

### "ModuleNotFoundError"
Make sure you ran `pip install -e .` from inside the project folder.
