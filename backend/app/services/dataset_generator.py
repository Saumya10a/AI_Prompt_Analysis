import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class DatasetGenerator:
    def __init__(self, output_path: str, num_records: int = 100_000, seed: int = 42):
        self.output_path = Path(output_path)
        self.num_records = num_records
        self.random = random.Random(seed)
        
        # 7 distinct categories spanning school students, college students, older adults, and technical domains
        self.categories = [
            "School & Homework",
            "College & Academic Study",
            "Senior & Everyday Assistance",
            "Creative Writing & Hobbies",
            "Programming & Software",
            "Data Processing & Analytics",
            "Daily Productivity & Planning"
        ]
        
        # Exact 7 models preserved
        self.models = [
            "gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", 
            "gemini-pro", "llama-2-70b", "mistral-large"
        ]

        # Distinct weights so volume distribution is varied and realistic
        self.category_weights = [18, 16, 14, 13, 15, 12, 12]
        self.model_weights = [18, 22, 10, 14, 14, 10, 12]

        # Model profiles: (token_multiplier, base_success_probability)
        self.model_profiles = {
            "gpt-4": (1.18, 0.95),
            "gpt-3.5-turbo": (0.82, 0.88),
            "claude-3-opus": (1.28, 0.96),
            "claude-3-sonnet": (1.04, 0.93),
            "gemini-pro": (0.92, 0.90),
            "llama-2-70b": (1.08, 0.86),
            "mistral-large": (0.88, 0.89),
        }

        # Category profiles: (token_scale, success_adjustment)
        # Allows average token count and success rate to vary significantly across task domains
        self.category_profiles = {
            "School & Homework": (0.85, 0.05),             # concise school prompts, high success (~96%)
            "College & Academic Study": (1.85, -0.07),     # long research prompts/answers, harder (~84%)
            "Senior & Everyday Assistance": (0.65, 0.06),  # simple, short, gentle advice, very high success (~97%)
            "Creative Writing & Hobbies": (1.30, 0.03),    # medium-long stories/recipes, high success (~94%)
            "Programming & Software": (1.65, -0.10),       # code blocks, strict syntax, lower success (~81%)
            "Data Processing & Analytics": (1.45, -0.05),  # SQL queries, statistics, moderate success (~86%)
            "Daily Productivity & Planning": (0.95, 0.04), # short emails, schedules, high success (~95%)
        }

        self.category_data = {
            "School & Homework": {
                "prompts": [
                    "Explain the process of photosynthesis step-by-step for a 6th grade science project.",
                    "Help me solve the algebra equation 3x + 7 = 28 with each step clearly written.",
                    "Write a 4-line rhyming poem about rainy days for my school English homework.",
                    "What are the eight planets in our solar system in order from the Sun?",
                    "Check my spelling and grammar for this short essay about my pet dog.",
                    "Why is the sky blue during the day and orange at sunset? Explain simply.",
                    "Summarize the story of Romeo and Juliet in 3 simple paragraphs for middle school.",
                    "How do plants absorb water from the soil through their roots?"
                ],
                "responses": [
                    "Photosynthesis is how green plants turn sunlight, water, and carbon dioxide into oxygen and food (glucose). Chlorophyll inside leaves traps the sunlight to power this chemical reaction.",
                    "Step 1: Subtract 7 from both sides: 3x = 21. Step 2: Divide both sides by 3: x = 7. The final solution is x = 7.",
                    "Dark clouds roll across the sky so gray, / Soft raindrops wash the dusty road away. / Puddles splash beneath our running feet, / Bringing cool winds down the quiet street.",
                    "The eight planets in order from the Sun are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. (Pluto is classified as a dwarf planet).",
                    "Here is your corrected essay: punctuation and subject-verb agreements have been fixed, and transition words were added between paragraphs.",
                    "Sunlight scatters when it hits gases in the atmosphere. Blue light has short waves and scatters in all directions during the day. At sunset, light travels through thicker air, leaving longer red and orange wavelengths."
                ],
                "failures": [
                    "Error: Unable to compute algebraic solution due to missing equation operators.",
                    "Failed: Essay text was incomplete or missing; could not complete grammatical review."
                ]
            },
            "College & Academic Study": {
                "prompts": [
                    "Summarize the methodology and empirical findings of this research paper on solar energy adoption.",
                    "Draft a formal academic email to Professor Higgins requesting a 48-hour extension on my midterm paper.",
                    "Compare qualitative versus quantitative research methodologies and discuss when each is appropriate in sociology.",
                    "Explain Keynesian economic stimulus versus classical monetarism during periods of stagflation.",
                    "Outline a literature review matrix comparing transformer architectures for natural language processing.",
                    "Derive the differential equation for damped harmonic motion and define the critical damping factor."
                ],
                "responses": [
                    "The empirical analysis investigates residential solar adoption across 1,400 households using difference-in-differences econometric modeling. Results demonstrate a 23% increase in adoption following municipal rebate subsidies.",
                    "Dear Professor Higgins, I am writing to respectfully request a 48-hour extension on the midterm submission due to conflicting lab commitments. I have completed the primary literature review and outline.",
                    "Quantitative methodology relies on numerical measurement and inferential statistics to test hypotheses across large samples. Qualitative methodology utilizes semi-structured interviews and thematic analysis to understand human lived experiences.",
                    "Keynesian theory advocates government fiscal intervention and deficit spending to stimulate aggregate demand, whereas monetarism maintains that stable money supply growth is the primary determinant of price stability."
                ],
                "failures": [
                    "Error: Citation lookup failed; unable to verify peer-reviewed empirical methodology.",
                    "Failed: Mathematical derivation incomplete due to unresolved boundary condition singularity."
                ]
            },
            "Senior & Everyday Assistance": {
                "prompts": [
                    "How do I make the font size bigger and easier to read on my smartphone screen?",
                    "How can I tell if a phone call or text message asking for bank details is a scam?",
                    "Explain what blood pressure numbers like 120 over 80 mean in plain words without medical jargon.",
                    "Write a warm and loving birthday message for my 12-year-old grandson.",
                    "What are gentle seated exercises to relieve morning knee and hip joint stiffness?",
                    "How do I start a video call with my family using WhatsApp on an iPad?",
                    "Can you give me simple tips to stay hydrated and avoid dizziness during hot summer days?"
                ],
                "responses": [
                    "To increase text size on your phone: Open Settings, tap Display, then select Font Size. Slide the circle to the right until the letters look comfortably large and clear.",
                    "Legitimate banks will never call or text asking for your PIN, password, or urgent money transfers. If someone pressures you, hang up immediately and call the number on the back of your card.",
                    "The top number (systolic) measures the pressure in your arteries when your heart beats. The bottom number (diastolic) measures the resting pressure between beats. 120/80 is considered a healthy baseline.",
                    "Happy 12th Birthday to my wonderful grandson! Watching you grow into such a kind, thoughtful, and bright young person fills my heart with immense pride and joy. Sending you all my love!",
                    "Try gentle seated ankle circles, smooth heel-to-toe foot rocking, and seated knee lifts while holding the chair armrests. Do 10 slow repetitions each without forcing any movement."
                ],
                "failures": [
                    "Unable to complete device guidance. Please verify the device make and operating system version.",
                    "Error: Audio/video permissions setting could not be confirmed for this application."
                ]
            },
            "Creative Writing & Hobbies": {
                "prompts": [
                    "Write an easy homemade vegetable soup recipe using potatoes, carrots, celery, and garlic.",
                    "Suggest 5 beginner-friendly indoor house plants that thrive in low light.",
                    "Draft a relaxing 3-day itinerary for an autumn weekend getaway in the mountain hills.",
                    "Write a whimsical bedtime story about an owl who wanted to learn how to bake sourdough bread.",
                    "Brainstorm 8 warm and inviting names for a neighborhood weekend book and tea club."
                ],
                "responses": [
                    "Warm Vegetable Soup: Saute diced onion, garlic, carrots, and celery in olive oil for 8 minutes. Add cubed potatoes, vegetable broth, and thyme. Simmer for 25 minutes until tender, then season with sea salt and cracked black pepper.",
                    "Top 5 low-light house plants: 1. Snake Plant (Sansevieria), 2. ZZ Plant (Zamioculcas), 3. Golden Pothos, 4. Cast Iron Plant, and 5. Peace Lily. Water sparingly when the top soil dries out.",
                    "Day 1: Scenic cabin check-in, valley stroll, and dinner by the hearth. Day 2: Morning botanical trail walk, local cider tasting, and stargazing. Day 3: Artisan farmers market and scenic overlook drive."
                ],
                "failures": [
                    "Error: Generation truncated due to context window boundary.",
                    "Failed: Unable to synthesize creative prompt with provided constraints."
                ]
            },
            "Programming & Software": {
                "prompts": [
                    "Write a Python function to sort a list of dictionaries by a specified key and handle missing keys.",
                    "Debug this React useEffect hook that causes an infinite re-rendering cycle.",
                    "Create a RESTful API endpoint in FastAPI with Pydantic request validation and error handling.",
                    "Design a normalized PostgreSQL schema for a multi-tenant subscription billing platform.",
                    "Compare microservices architecture with modular monolithic architecture for early-stage startups."
                ],
                "responses": [
                    "Here is the Python function using operator.itemgetter with default fallbacks: def sort_dicts(records, key, default=None): return sorted(records, key=lambda x: x.get(key, default)).",
                    "The infinite re-render occurs because an object literal is declared inside the component body and passed into the useEffect dependency array, creating a new reference on every render cycle.",
                    "This FastAPI route defines POST /api/subscriptions with Pydantic BaseModel validation, HTTP 422 error handlers, and asynchronous database session transactions."
                ],
                "failures": [
                    "Error: SyntaxError or unhandled KeyError raised during script execution.",
                    "Failed: Unit tests failed with 2 assertions unsatisfied in concurrency test suite."
                ]
            },
            "Data Processing & Analytics": {
                "prompts": [
                    "Write an optimized SQL window query to calculate monthly customer retention cohorts.",
                    "How do I detect and impute missing numerical values in a pandas DataFrame using median substitution?",
                    "Explain the difference between inner join, left outer join, and full outer join with a table example.",
                    "Write a PySpark aggregation pipeline to compute session duration and page views per user."
                ],
                "responses": [
                    "This query partitions transactions by user_id and month using DATE_TRUNC, then utilizes LAG(month, 1) to determine active repeat retention across successive cohorts.",
                    "Use df[col] = df[col].fillna(df[col].median()) to perform median imputation, which is resilient against extreme outliers compared to standard arithmetic mean imputation.",
                    "An inner join returns only rows with matching keys in both tables. A left outer join retains all left records, populating unmatched right attributes with NULL values."
                ],
                "failures": [
                    "Failed: OutOfMemory exception encountered during distributed shuffle stage.",
                    "Error: Invalid SQL syntax near GROUP BY clause in subquery alias."
                ]
            },
            "Daily Productivity & Planning": {
                "prompts": [
                    "Draft a polite professional message informing my team that I will be out of office tomorrow.",
                    "Create a balanced weekly meal prep schedule and organized grocery checklist for a family of four.",
                    "Summarize these messy meeting notes into 4 clear action items with owners and deadlines.",
                    "How can I structure my morning work routine to minimize distractions and stay organized?"
                ],
                "responses": [
                    "Hi team, please note that I will be out of office tomorrow, Thursday. I will have limited email access; for any urgent questions, please connect with Sarah. Thanks!",
                    "Weekly Meal Schedule: Mon - Mediterranean grain bowls; Tue - Sheet-pan lemon herb chicken; Wed - Lentil vegetable curry; Thu - Turkey tacos; Fri - Homemade flatbread pizza with fresh greens.",
                    "Action Item 1: Marcus to finalize user acceptance tests by Wednesday. Action Item 2: Elena to update API documentation by Friday. Action Item 3: Dev team to deploy staging build."
                ],
                "failures": [
                    "Error: Insufficient input provided to extract meeting action items.",
                    "Failed: Scheduling conflict detected between calendar constraints."
                ]
            }
        }
    
    def _generate_timestamp(self, start_date: datetime, end_date: datetime) -> datetime:
        time_between = end_date - start_date
        days_between = max(1, time_between.days)
        random_days = self.random.randrange(days_between)
        return start_date + timedelta(days=random_days)
    
    def _count_tokens(self, text: str) -> int:
        return max(1, len(text.split()))
    
    def generate_record(self, index: int) -> Dict[str, Any]:
        category = self.random.choices(self.categories, weights=self.category_weights, k=1)[0]
        model = self.random.choices(self.models, weights=self.model_weights, k=1)[0]

        cat_data = self.category_data[category]
        prompt = self.random.choice(cat_data["prompts"])

        # Category and model profile parameters
        cat_scale, success_adj = self.category_profiles[category]
        model_scale, base_succ = self.model_profiles[model]

        effective_success = min(0.99, max(0.68, base_succ + success_adj))
        success = self.random.random() < effective_success

        if success:
            response = self.random.choice(cat_data["responses"])
        else:
            response = self.random.choice(cat_data["failures"])

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        timestamp = self._generate_timestamp(start_date, end_date)

        # Token count reflects both category content complexity and model verbosity
        base_tokens = self._count_tokens(prompt + " " + response)
        token_count = max(8, round(base_tokens * cat_scale * model_scale + self.random.randint(0, 10)))
        
        return {
            "prompt": prompt,
            "response": response,
            "model": model,
            "category": category,
            "timestamp": timestamp.isoformat(),
            "token_count": token_count,
            "success": success
        }
    
    def generate_dataset(self) -> List[Dict[str, Any]]:
        records = []
        for i in range(self.num_records):
            record = self.generate_record(i)
            records.append(record)
        return records
    
    def save_dataset(self, records: List[Dict[str, Any]]):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
    
    def generate_and_save(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for index in range(self.num_records):
                f.write(json.dumps(self.generate_record(index)) + '\n')
        return self.num_records

