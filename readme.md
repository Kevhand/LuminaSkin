# LuminaSkin

### An AI-powered skincare platform that combines skin analysis, personalized recommendations, and intelligent conversational guidance.


## Overview

LuminaSkin is an AI-powered personalized skincare platform designed to help users understand their skin, track changes over time, and make better skincare decisions.

Instead of treating the AI assistant as a standalone chatbot, LuminaSkin builds a structured understanding of each user through their skin profile, lifestyle, skincare routine, products, goals, allergies, budget, and skin analysis results.

This information is actively used by the AI to personalize its responses. The more relevant information available about the user, the better the assistant can understand their situation and provide targeted guidance for their specific skin concerns.

Users can also update their information directly through conversation. For example, instead of navigating to their profile and manually changing their lifestyle information, a user can simply tell the assistant:

> "I stopped smoking."

The AI can interpret the message and update the corresponding structured user information, allowing that change to influence future recommendations and conversations.

LuminaSkin combines this evolving user context with skin analysis, conversation history, and current external information when necessary to provide personalized, actionable skincare guidance.



## Key Features

### 🧠 An AI That Understands the User

LuminaSkin uses information provided by the user — including their skin profile, lifestyle, skincare routine, products, goals, allergies, budget, and skin analysis results — as meaningful context for its AI assistant.

This allows the assistant to give guidance based on the user's actual situation rather than generic skincare advice.

For example, if a user is already using a salicylic acid treatment, the assistant can take that into account when suggesting changes instead of simply recommending another exfoliant.

### 💬 Conversational Profile & Routine Updates

Users don't always need to navigate through profile or routine pages to keep their information up to date.

They can update their structured information directly through the AI assistant.

For example:

> "I stopped smoking."

or:

> "I started using a new moisturizer."

The assistant can interpret these conversational updates and reflect them in the user's structured lifestyle, routine, or product information.

These updates then become part of the context used in future conversations and recommendations.

### 🔬 Skin Analysis

LuminaSkin provides AI-assisted skin analysis with:

- Multiple skin concern detection
- Individual concern scores
- Overall skin score
- Skin age estimation
- Visual overlays showing where detected concerns occur
- Historical scan tracking

### 📈 Progress & Insights

Users can track how their skin changes over time through:

- Overall score trends
- Individual concern trends
- Skin age changes
- Historical scan data
- Visual analytics and graphs
- Downloadable PDF reports

### 🎯 Personalized Skincare Guidance

The assistant combines relevant user information with skin analysis results to provide guidance tailored to the user's current situation.

Recommendations can take into account:

- Existing skincare routine
- Products already being used
- Lifestyle factors
- Skin concerns
- Allergies
- Budget
- Previous skin analysis results

### 🌐 Current Information When Needed

For questions requiring up-to-date or externally verifiable information, the AI can use Google Search to retrieve current information instead of relying solely on its existing knowledge.

Search is used selectively rather than for information that is already available in the user's LuminaSkin context.

### 🛡️ Responsible AI Guidance

LuminaSkin includes safeguards designed for skincare-related conversations:

- Does not diagnose medical conditions
- Does not prescribe medication
- Distinguishes observations from certainty
- Recommends professional dermatological advice for severe or persistent concerns
- Does not invent user-specific scan results or products
- Checks relevant user constraints such as allergies and budget before making recommendations




## How It Works

LuminaSkin is built around a continuous feedback loop between the user's skin data, everyday information, and the AI assistant.

### 1. Build Your Skin Profile

Users provide information such as their skincare goals, lifestyle, routine, products, allergies, and budget.

This information becomes structured user context that can be used by the AI when providing personalized guidance.

### 2. Start a Skin Analysis

Users upload a clear image of their face and select the skin concerns they want to analyze.

The image quality and selected concerns determine the analysis performed on the uploaded image.

### 3. Receive Skin Analysis Results

Once the analysis is complete, LuminaSkin provides:

- Overall skin score
- Skin age
- Individual scores for selected skin concerns
- Visual overlays showing where detected concerns occur
- Detailed scan results

Users can view their results and understand which areas of their skin need the most attention.

### 4. Track Skin Progress

Every completed scan is stored in the user's scan history.

Users can compare their results over time through:

- Overall score trends
- Individual concern trends
- Skin age changes
- Historical scan results
- Graphs and visual analytics

Users can also generate and download a PDF report containing their skin analysis and relevant insights.

### 5. Build an AI Understanding of the User

LuminaSkin combines information from different parts of the user's profile, including:

- Skin analysis
- Skin profile
- Lifestyle
- Skincare routine
- Products
- Previous conversations

This information is used as meaningful context for the AI rather than simply being stored as profile data.

### 6. Ask the AI

Users can ask questions naturally through the LuminaSkin AI assistant.

For example:

> "Why are my dark circles getting worse?"

The assistant can use the user's relevant scan results, lifestyle information, routine, products, and recent conversation history to provide a personalized response.

### 7. Update Your Information Through Conversation

Users don't always need to navigate back to their profile or routine pages to update their information.

They can simply tell the AI about a change.

For example:

> "I've started using sunscreen every morning."

or:

> "I stopped smoking."

The assistant can interpret these updates and modify the relevant structured information, allowing the change to influence future recommendations and conversations.

### 8. Get Personalized Guidance

The assistant uses the relevant user context to provide actionable guidance for the user's specific situation.

When a question requires current or externally verifiable information, LuminaSkin can use Google Search to retrieve up-to-date information.

This creates a continuous loop:

User Information  
↓  
Skin Analysis  
↓  
AI Understanding  
↓  
Personalized Guidance  
↓  
Profile & Routine Updates  
↓  
Better Future Guidance


## AI Architecture

LuminaSkin uses a multi-stage AI pipeline rather than sending the user's entire database directly to a language model.

When a user sends a message, it passes through several stages:

```text
User Message
     │
     ▼
Module Planner
     │
     │ Determines what information is relevant
     ▼
Context Selector
     │
     │ Selects relevant user context
     ▼
Context Assembly
     │
     │ Profile + scans + routine + products
     │ + lifestyle + relevant conversation history
     ▼
AI Reasoner
     │
     ├── Gemini
     │
     ├── Model fallback
     │
     └── Google Search when current information is required
     │
     ▼
Personalized Response
```


### Module Planner
The planner analyzes the user's message and determines which parts of the user's information may be relevant.
For example, a question about:

"Why are my dark circles getting worse?"
may require skin analysis and lifestyle information, while a question about:

"Is my moisturizer compatible with my current routine?"
may require product and routine information.

### Context Selection
Only the relevant information is selected and passed forward to the final reasoning model.
This avoids unnecessarily sending the user's entire stored profile with every request and allows the assistant to focus on the context that matters for the current question.

### Conversation History
LuminaSkin maintains recent conversation history so that the assistant can understand the immediate context of an ongoing conversation.
The most recent messages are included alongside the selected user context when relevant.

### AI Reasoner
The final reasoning stage uses Gemini to generate the response based on the assembled context.
The reasoner also includes a model fallback mechanism so that if one configured model fails, another available model can be attempted.

### Search Grounding
Google Search is available to the final reasoning stage when the question requires current or externally verifiable information.
Search is intentionally not used when the answer can already be determined from the user's LuminaSkin context or reliable general knowledge.

### Structured Updates
The AI assistant can also interpret conversational updates and modify the user's structured information when appropriate.
For example:

```text
"I stopped smoking"
        │
        ▼
AI understands the update
        │
        ▼
Lifestyle data is updated
        │
        ▼
Updated information becomes available
to future AI conversations
```


## Skin Analysis & Progress Tracking

LuminaSkin's skin analysis is designed to help users understand their current skin condition and track how it changes over time.

### Image-Based Skin Analysis

Users upload a clear facial image and select the skin concerns they want to analyze.

The selected concerns are sent for analysis, allowing LuminaSkin to evaluate the requested areas and generate individual concern scores.

### Analysis Results

After the analysis is completed, users can view:

- Overall skin score
- Skin age
- Individual skin concern scores
- Concern status
- Visual mask overlays
- Visual overlays highlighting detected areas

The visual overlays allow users to see where a particular concern was detected rather than relying only on numerical scores.

### Scan History

Completed scans are stored in the user's scan history.

Users can revisit previous analyses and track changes in:

- Overall skin score
- Skin age
- Individual concern scores
- Selected skin concerns
- Analysis results

### Progress Analytics

Historical scan data is used to generate visual trends and analytics, helping users identify whether their skin concerns are improving, worsening, or remaining relatively stable over time.

### PDF Reports

Users can generate downloadable PDF reports containing their skin analysis results and relevant visualizations.

This provides users with a convenient record of their assessments and progress.





## Personalized Skincare Guidance

LuminaSkin uses the information collected throughout the platform to provide guidance tailored to the individual user rather than generic skincare recommendations.

### Personalized Recommendations

The AI can consider relevant information such as:

- Skin analysis results
- Skin concerns and their scores
- Skin type
- Skincare goals
- Existing skincare routine
- Products currently being used
- Lifestyle factors
- Allergies
- Budget
- Previous conversations

This allows recommendations to be based on the user's actual circumstances and existing habits.

### Context-Aware Recommendations

The AI does not simply recommend products or ingredients based on a skin concern in isolation.

It considers the user's existing routine and products when suggesting changes.

For example, if a user is already using a salicylic acid treatment, the assistant can avoid unnecessarily recommending another exfoliating product.

### Actionable Guidance

Rather than only explaining what a skin concern is, LuminaSkin aims to help users understand:

- What may be contributing to the concern
- Which habits may be relevant
- What changes could be considered
- How existing products or routines may affect the recommendation
- Which changes should be prioritized

The goal is to help users make practical improvements to their skincare routine and lifestyle over time.

### Continuous Personalization

As users update their profile, lifestyle, routine, and products — either manually or through conversation — the updated information becomes available as context for future AI interactions.

This allows LuminaSkin's guidance to evolve alongside the user.



## Tech Stack

### Backend

- Python
- Django
- Django ORM
- SQLite / PostgreSQL
- Gunicorn
- WhiteNoise

### AI

- Google Gemini
- Google Search
- Multi-stage AI planning and context selection
- Structured user-context management

### Skin Analysis

- YouCam API
- Image processing with Pillow
- NumPy

### Data & Analytics

- Pandas
- Matplotlib
- Plotly

### Reports

- ReportLab
- PyPDF2 / pypdf

### Frontend

- HTML
- CSS
- JavaScript
- Django Templates

### APIs & Services

- Google Gemini API
- MakeupAR Skin Analysis API




## Project Structure

```text
LuminaSkin/
├── LuminaSkin/                  # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── skin/                        # Main Django application
│   ├── ai/                      # AI pipeline and reasoning
│   │   ├── module_selector.py
│   │   ├── select_context.py
│   │   ├── build_ai_context.py
│   │   ├── chat_engine.py
│   │   ├── chat.py
│   │   ├── prompt_builder.py
│   │   ├── prompts.py
│   │   ├── routine_updater.py
│   │   ├── trend_engine.py
│   │   ├── analytics.py
│   │   ├── generate_ai_report.py
│   │   ├── generate_report_data.py
│   │   └── pdf.py
│   │
│   ├── models/                  # Database models
│   │   ├── profile.py
│   │   ├── detailed_skin_profile_info.py
│   │   ├── scan.py
│   │   ├── chat.py
│   │   └── ai.py
│   │
│   ├── forms/                   # Django forms
│   │   ├── profile_forms.py
│   │   ├── detailed_skin_profile_info_forms.py
│   │   └── scan_forms.py
│   │
│   ├── reports/                 # Reports and visualization
│   │   ├── charts.py
│   │   └── pdf_report.py
│   │
│   ├── static/                  # CSS and JavaScript
│   │   ├── css/
│   │   └── js/
│   │
│   ├── templates/               # Django HTML templates
│   │   └── skin/
│   │
│   ├── view_functions/          # Separated view logic
│   │   └── profile.py
│   │
│   ├── api_call.py              # Skin analysis API integration
│   ├── utils.py                 # Utility functions
│   ├── views.py                 # Application views
│   ├── urls.py                  # Application URLs
│   ├── admin.py
│   └── apps.py
│
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```


## Setup & Installation

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or higher
- Git
- pip

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LuminaSkin
```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment so that LuminaSkin's dependencies remain isolated from other Python projects.

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell does not allow script execution, you can use:

```cmd
venv\Scripts\activate.bat
```

### 3. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

LuminaSkin requires API credentials and a Django secret key.
Create a `.env` file in the project root:

```text
LuminaSkin/
├── .env
├── .env.example
├── manage.py
└── ...
```

Add the required variables:

```env
SECRET_KEY=your-django-secret-key
API_KEY=your-youcam-api-key
GOOGLE_API_KEY=your-google-gemini-api-key
```

**Django Secret Key**
Generate a secure Django secret key using:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into your `.env` file:

```env
SECRET_KEY=generated-secret-key
```

*Do not use a secret key from the README or .env.example.*

**Gemini API Key**
LuminaSkin uses Google's Gemini API for its AI reasoning and conversational assistant.
Create a Google AI API key through Google AI Studio and add it to:

```env
GOOGLE_API_KEY=your-google-api-key
```

*Do not commit this key to the repository.*

**YouCam API Key**
LuminaSkin uses the YouCam API for image-based skin analysis.
Add the provided API key to:

```env
API_KEY=your-youcam-api-key
```

*The key is used for authenticated requests to the skin analysis service.*

### 5. Database Setup

After installing the dependencies and configuring the environment variables, apply the existing migrations:

```bash
python manage.py migrate
```

If you make changes to Django models during development, create new migrations with:

```bash
python manage.py makemigrations
```

Then apply them:

```bash
python manage.py migrate
```

### 6. Create an Admin Account

To access the Django administration interface, create a superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter the username, email address, and password.

### 7. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at:
`http://127.0.0.1:8000/`

### 8. Development Workflow

A typical development workflow is:

```powershell
# Activate environment
venv\Scripts\Activate.ps1

# Install/update dependencies
pip install -r requirements.txt

# After changing models
python manage.py makemigrations
python manage.py migrate

# Start the application
python manage.py runserver
```

### Environment Variables

The following environment variables are required:

| Variable | Purpose |
| :--- | :--- |
| `SECRET_KEY` | Django application security |
| `API_KEY` | YouCam API authentication |
| `GOOGLE_API_KEY` | Google Gemini API authentication |

**Security Note:** Never commit `.env` to Git. Store real API keys and secret values only in your local `.env` file or your deployment environment.



## Limitations

- Skin analysis results are intended for skincare guidance and are not a medical diagnosis.
- AI-generated recommendations may not always be suitable for every individual and should not replace professional dermatological advice.
- Skin analysis quality depends on the quality and clarity of the uploaded image.
- The AI's recommendations depend on the accuracy and completeness of the information provided by the user.
- Current information and product-related recommendations may depend on the availability and reliability of external search results.
- The application currently relies on external services such as the YouCam Skin Analysis API and Google Gemini API.


## Future Improvements

- Improve the accuracy and consistency of personalized skincare recommendations.
- Expand conversational profile updates to support more user information and actions.
- Improve long-term progress analysis by identifying trends across multiple skin scans.
- Expand the range of skin concerns supported by the analysis system.
- Further improve the AI's ability to combine skin analysis, lifestyle, routine, and product information.
- Add more robust validation and handling for uploaded images and external API failures.
- Improve the conversational experience with richer interactions and more detailed AI-generated insights.



## Author

**Yash Singh**

Computer Science & Engineering — AI & ML

---

If you found this project interesting or have suggestions, feel free to reach out.

