import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from ..models.schemas import PromptInspectionResult, ScoreBreakdown, ModelRecommendation


class PromptAnalyzer:
    def __init__(self):
        self._constraint_patterns = [
            r'(?:within|under|less than|at most|maximum|max)\s+(\d+)\s*(?:words?|characters?|chars?|sentences?|paragraphs?)',
            r'(?:at least|minimum|min|more than|over)\s+(\d+)\s*(?:words?|characters?|chars?|sentences?|paragraphs?)',
            r'(?:between|from)\s+(\d+)\s*(?:and|to)\s+(\d+)\s*(?:words?|characters?|chars?)',
            r'(?:exactly|precisely)\s+(\d+)\s*(?:words?|characters?|chars?)',
            r'(?:exactly|precisely|in)\s+(\d+)\s+(?:points?|items?|steps?|sections?|paragraphs?)',
            r'(?:step[- ]by[- ]step|stepwise)',
            r'(?:in simple words?|in plain english|for beginners?|without (?:any )?jargon)',
            r'\b(?:without|no|excluding)\s+(?:a\s+)?(?:third\s+variable|temporary\s+variable|temp\s+variable|extra\s+space|extra\s+memory|additional\s+variable|extra\s+variable|libraries?|builtin|built-in|helper|loop|recursion)\b',
            r'\b(?:without\s+using\s+[\w\s]{2,20}|without\s+[\w\s]{2,20}\s+variable)\b',
            r'\b(?:in[- ]place|constant\s+space|o\(1\)|o\(n\)|time\s+complexity|space\s+complexity)\b',
            r'\b(?:essay|poem|letter|speech|story|recipe|outline)\b',
        ]
        
        self._formatting_patterns = [
            r'(?:use|format as|in|as)\s+(?:markdown|md|html|json|xml|yaml|csv|plain text|essay|python|java|c\+\+|javascript)',
            r'(?:include|add|show)\s+(?:code blocks?|code snippets?|examples?)',
            r'(?:numbered|bulleted|bullet)\s+list',
            r'(?:table|tabular)\s+format',
        ]
        
        # Broad action verbs including everyday, educational, DSA, and technical prompts
        self._action_verbs = [
            'explain', 'describe', 'analyze', 'compare', 'evaluate', 'summarize',
            'create', 'generate', 'write', 'list', 'identify', 'calculate',
            'recommend', 'suggest', 'optimize', 'improve', 'fix', 'debug',
            'help', 'solve', 'draft', 'check', 'correct', 'outline', 'teach',
            'show', 'clarify', 'translate', 'remind', 'organize', 'plan', 'compose',
            'swap', 'implement', 'code', 'reverse', 'sort', 'search', 'traverse', 'build'
        ]

        self._conversational_starters = [
            'how do i', 'how to', 'how can i', 'what is', 'what are', 'why is',
            'why does', 'can you', 'could you', 'please', 'write me', 'write a', 'give me', 'help me'
        ]

        # Audience patterns
        self._audience_indicators = {
            "School Student (K-12)": [
                r'\b(?:essay|favourite festival|favorite festival|my school|my pet|my family|summer vacation|science project|6th|7th|8th|9th|10th|5th|middle school|high school|grade \d+|elementary|homework|rhyming poem|school project|for kids)\b'
            ],
            "College & University": [
                r'\b(?:college|university|professor|thesis|dissertation|midterm|research paper|literature review|apa format|ieee|citation|academic|macroeconomics|econometrics)\b'
            ],
            "Senior & Everyday Assistance": [
                r'\b(?:font size|screen size|scam|phishing|blood pressure|grandson|granddaughter|stiff joints|medication|plain words|without jargon|smartphone|older adult|elderly)\b'
            ],
            "Developer & CS Student": [
                r'\b(?:code|coding|program|programming|script|swap|variable|variables|dsa|leetcode|algorithm|syntax|python|java|cpp|c\+\+|javascript|sql|function|array|linked\s*list|binary\s*tree|recursion|loop|debug|endpoint|api|database|in-place)\b'
            ]
        }

    
    def _count_words(self, text: str) -> int:
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _count_characters(self, text: str) -> int:
        return len(text)
    
    def _detect_code_blocks(self, text: str) -> int:
        patterns = [
            r'```[\s\S]*?```',
            r'`[^`]+`',
            r'<code>[\s\S]*?</code>',
        ]
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text))
        return count
    
    def _extract_constraints(self, text: str) -> List[str]:
        constraints = []
        text_lower = text.lower()
        
        for pattern in self._constraint_patterns + self._formatting_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                matched_str = match.group(0).strip()
                if matched_str:
                    constraints.append(matched_str)
        
        return list(dict.fromkeys(constraints))

    def _detect_audience_and_age(self, text: str) -> Tuple[str, str]:
        text_lower = text.lower()
        for audience, patterns in self._audience_indicators.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    if audience == "School Student (K-12)":
                        return audience, "School Student (Approx. 8–15 yrs)"
                    elif audience == "College & University":
                        return audience, "College / Young Adult (Approx. 18–24 yrs)"
                    elif audience == "Senior & Everyday Assistance":
                        return audience, "Older Adult / Senior (Approx. 60+ yrs)"
                    elif audience == "Developer & CS Student":
                        return audience, "CS Student / Developer (Approx. 18–35 yrs)"
        return "General Audience", "General Audience (All Ages)"

    def _detect_intent(self, text: str) -> str:
        text_lower = text.lower()
        if any(term in text_lower for term in ['swap', 'variable', 'dsa', 'leetcode', 'in-place', 'binary search', 'linked list', 'recursion']):
            return "DSA & Algorithmic Implementation"
        if any(term in text_lower for term in ['code', 'python', 'sql', 'debug', 'function', 'api', 'react', 'algorithm', 'script', 'program']):
            return "Programming & Software Implementation"
        if any(term in text_lower for term in ['essay', 'story', 'poem', 'write an essay', 'write me an essay', 'draft an essay']):
            return "Creative Writing & Essay Drafting"
        if any(term in text_lower for term in ['explain', 'what is', 'what are', 'why is', 'why does', 'how does', 'summarize', 'compare']):
            return "Explanation & Conceptual Learning"
        if any(term in text_lower for term in ['solve', 'calculate', 'homework', 'equation', 'algebra', 'math']):
            return "Homework & Problem Solving"
        if any(term in text_lower for term in ['scam', 'font size', 'phone', 'whatsapp', 'exercise', 'stiffness', 'grandson', 'settings', 'how do i', 'how to']):
            return "Everyday & Device Guidance"
        if any(term in text_lower for term in ['recipe', 'itinerary', 'trip', 'write a', 'draft']):
            return "Creative & Composition"
        return "General Query"

    def _recommend_model(self, audience: str, intent: str, text: str) -> ModelRecommendation:
        text_lower = text.lower()

        # 1. DSA & Algorithmic tasks (Strict constraints, in-place math, bitwise tricks)
        if "DSA" in intent or any(w in text_lower for w in ['swap', 'without a third variable', 'in-place', 'binary search', 'recursion', 'time complexity']):
            return ModelRecommendation(
                recommended_model="gpt-4",
                secondary_model="claude-3-opus",
                reason="Excels at edge-case logic, algorithmic tricks (e.g. arithmetic + / - or XOR bitwise swaps without third variables), and zero syntax bugs.",
                trade_off="Ensures mathematical and algorithmic correctness for coding interview standards."
            )

        # 2. General Programming & Software Development
        if "Programming" in intent or any(w in text_lower for w in ['python', 'sql', 'debug', 'fastapi', 'react', 'algorithm']):
            return ModelRecommendation(
                recommended_model="gpt-4",
                secondary_model="claude-3-opus",
                reason="Superior syntactical accuracy, robust edge-case handling, and deep architectural debugging capabilities.",
                trade_off="Longer generation time, but drastically reduces code defects and logic bugs."
            )

        # 3. School essays and creative student tasks
        if "Essay Drafting" in intent or ("School" in audience and any(w in text_lower for w in ['essay', 'poem', 'story', 'festival'])):
            return ModelRecommendation(
                recommended_model="gpt-3.5-turbo",
                secondary_model="claude-3-sonnet",
                reason="Excels at natural narrative prose, creative storytelling, and age-appropriate vocabulary with very fast response times.",
                trade_off="Significantly faster and more cost-effective than heavy reasoning engines (like GPT-4) while producing lively, fluent essays."
            )

        # 4. College & Academic research
        if "College" in audience or any(w in text_lower for w in ['research paper', 'thesis', 'literature review', 'econometrics', 'derive']):
            return ModelRecommendation(
                recommended_model="gpt-4",
                secondary_model="claude-3-opus",
                reason="State-of-the-art multi-step academic reasoning, rigorous conceptual synthesis, and formal scholarly nuance.",
                trade_off="Slightly higher compute cost and latency, but essential for academic rigor and factual precision."
            )

        # 5. Senior Citizen & Everyday Assistance
        if "Senior" in audience or any(w in text_lower for w in ['font size', 'scam', 'blood pressure', 'plain words', 'without jargon']):
            return ModelRecommendation(
                recommended_model="claude-3-sonnet",
                secondary_model="gemini-pro",
                reason="Renowned for empathetic, patient, clear instructions with zero confusing technical jargon.",
                trade_off="Focuses on conversational warmth and clear step-by-step guidance rather than terse technical shorthand."
            )

        # 6. Data Processing & Tabular Analytics
        if any(w in text_lower for w in ['sql', 'query', 'dataframe', 'pyspark', 'retention', 'impute']):
            return ModelRecommendation(
                recommended_model="gemini-pro",
                secondary_model="llama-2-70b",
                reason="Strong tabular query reasoning, SQL pattern understanding, and fast numerical synthesis.",
                trade_off="High throughput with solid analytical precision."
            )

        # 7. Daily Productivity & Workplace Communication
        if any(w in text_lower for w in ['email', 'out of office', 'meeting', 'agenda', 'schedule', 'action items']):
            return ModelRecommendation(
                recommended_model="mistral-large",
                secondary_model="gpt-3.5-turbo",
                reason="Crisp, efficient language generation that produces professional emails without unnecessary fluff.",
                trade_off="High speed and minimal token consumption."
            )

        # Default fallback recommendation
        return ModelRecommendation(
            recommended_model="gpt-3.5-turbo",
            secondary_model="claude-3-sonnet",
            reason="Well-rounded, versatile model offering high speed and balanced fluency for general prompts.",
            trade_off="Great generalist performance across diverse everyday inquiries."
        )
    
    def _evaluate_scores(self, text: str, audience: str, intent: str) -> Tuple[float, ScoreBreakdown]:
        text_lower = text.lower()
        words = self._count_words(text)

        # 1. Clarity & Intent (Max 0.35)
        clarity = 0.0
        # Check action verbs
        matched_verbs = [v for v in self._action_verbs if re.search(rf'\b{v}\b', text_lower)]
        if matched_verbs:
            clarity += min(0.20 + (len(matched_verbs) - 1) * 0.06, 0.26)
        
        # Check conversational or drafting request triggers
        if any(trigger in text_lower for trigger in self._conversational_starters) or '?' in text:
            clarity += 0.09
        
        # Explicit coding, DSA, essay, or creative request is crystal clear
        if any(k in text_lower for k in ["code", "swap", "algorithm", "function", "essay", "story", "recipe"]):
            clarity = max(clarity, 0.32)
        clarity = min(clarity, 0.35)

        # 2. Audience & Context (Max 0.25)
        context = 0.0
        if audience != "General Audience":
            context += 0.18
        if any(cue in text_lower for cue in ['variables', 'variable', 'a and b', 'without', 'for my', 'for a', 'in simple', 'plain english', 'without jargon', 'context', 'because', 'project', 'exam', 'homework', 'phone', 'on my', 'about my']):
            context += 0.07
        context = min(context, 0.25)

        # 3. Constraints & Formatting (Max 0.25)
        constraints = self._extract_constraints(text)
        constraint_score = min(len(constraints) * 0.12, 0.25)
        # Specific algorithmic exclusion (e.g. without third variable / in-place) is a strong constraint
        if any("without" in c for c in constraints) or any("in-place" in c for c in constraints):
            constraint_score = max(constraint_score, 0.20)

        # 4. Length & Detail Adequacy (Max 0.15)
        length_score = 0.0
        if words >= 4:
            length_score += 0.05
        if words >= 8:
            length_score += 0.05
        if words >= 18:
            length_score += 0.05

        total = round(min(clarity + context + constraint_score + length_score, 1.0), 2)
        breakdown = ScoreBreakdown(
            clarity_score=round(clarity, 2),
            context_score=round(context, 2),
            constraint_score=round(constraint_score, 2),
            length_score=round(length_score, 2)
        )
        return total, breakdown

    
    def _generate_improvement_hints(self, text: str, audience: str, intent: str) -> List[str]:
        hints = []
        words = self._count_words(text)
        text_lower = text.lower()
        constraints = self._extract_constraints(text)

        if "Essay" in intent or "essay" in text_lower:
            if not any(w in text_lower for w in ['words', 'paragraphs', 'pages', 'short', 'long']):
                hints.append("Specify an approximate length (e.g. 'in 250 words' or 'in 3 paragraphs') to match class requirements.")
            if "favourite" in text_lower or "favorite" in text_lower:
                hints.append("Mentioning your specific festival (e.g. Diwali, Christmas, Eid, or Halloween) gives more vibrant personal anecdotes.")
            return hints

        if words < 6:
            hints.append("Add a little more detail so the AI understands your specific goal.")
        
        has_verb = any(re.search(rf'\b{v}\b', text_lower) for v in self._action_verbs)
        has_question = any(trig in text_lower for trig in self._conversational_starters) or '?' in text
        if not has_verb and not has_question:
            hints.append("Include an action word (e.g., 'explain', 'show', 'write', 'solve') or question phrasing.")
        
        if audience == "General Audience":
            hints.append("Mention your audience or target level (e.g. 'for a 6th grader', 'in plain words for seniors', or 'for a college exam').")
        
        if not constraints:
            hints.append("Add format guidance if desired (e.g. 'step-by-step', 'in 3 bullet points', or 'under 100 words').")
        
        if 'example' not in text_lower and words >= 12:
            hints.append("Asking for 'a concrete example' can make explanations much easier to follow.")
        
        return hints
    
    def analyze(self, prompt: str) -> PromptInspectionResult:
        word_count = self._count_words(prompt)
        character_count = self._count_characters(prompt)
        code_blocks = self._detect_code_blocks(prompt)
        constraints = self._extract_constraints(prompt)
        audience, age_group = self._detect_audience_and_age(prompt)
        intent = self._detect_intent(prompt)
        specificity_score, score_breakdown = self._evaluate_scores(prompt, audience, intent)
        improvement_hints = self._generate_improvement_hints(prompt, audience, intent)
        model_rec = self._recommend_model(audience, intent, prompt)
        
        return PromptInspectionResult(
            original_prompt=prompt,
            word_count=word_count,
            character_count=character_count,
            code_blocks_detected=code_blocks,
            constraints_extracted=constraints,
            specificity_score=specificity_score,
            improvement_hints=improvement_hints,
            inspected_at=datetime.utcnow(),
            detected_intent=intent,
            detected_audience=audience,
            estimated_age_group=age_group,
            score_breakdown=score_breakdown,
            model_recommendation=model_rec
        )


