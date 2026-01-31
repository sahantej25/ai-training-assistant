"""
Guardrails Module for AI Training Assistant
Provides content safety, validation, and moderation
"""

from typing import Dict, List, Tuple
import re
from datetime import datetime, timedelta


class ContentGuardrails:
    """Content safety and moderation guardrails"""
    
    def __init__(self):
        """Initialize guardrails with rules and patterns"""
        
        # Sensitive topics to detect
        self.sensitive_patterns = {
            "personal_info": [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{16}\b',  # Credit card
                r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            ],
            "harmful_content": [
                r'\b(suicide|kill myself|end my life)\b',
                r'\b(hack|exploit|breach|steal)\b',
                r'\b(illegal|unlawful|criminal activity)\b',
            ],
            "inappropriate": [
                r'\b(offensive language|profanity)\b',
                # Add more as needed
            ]
        }
        
        # Blocked topics
        self.blocked_topics = [
            "personal medical advice",
            "legal advice",
            "financial investment advice",
            "how to commit crimes",
            "hacking tutorials",
            "dangerous activities"
        ]
        
        # Rate limiting tracking
        self.user_request_history = {}
        self.max_requests_per_minute = 10
        
        # Input validation limits
        self.max_input_length = 2000
        self.min_input_length = 3
        
        print("✅ Content Guardrails initialized")
    
    def validate_input(self, user_input: str, user_id: int = None) -> Tuple[bool, str]:
        """
        Validate user input before processing
        
        Args:
            user_input: User's question/message
            user_id: User ID for rate limiting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        
        # Check 1: Length validation
        if len(user_input) < self.min_input_length:
            return False, "⚠️ Your message is too short. Please provide more details."
        
        if len(user_input) > self.max_input_length:
            return False, f"⚠️ Your message is too long (max {self.max_input_length} characters). Please shorten it."
        
        # Check 2: Rate limiting
        if user_id:
            if not self._check_rate_limit(user_id):
                return False, "⚠️ Too many requests. Please wait a moment before trying again."
        
        # Check 3: Detect personal information
        has_personal_info, info_type = self._detect_personal_info(user_input)
        if has_personal_info:
            return False, f"⚠️ Please don't share {info_type} in your messages. This is for your safety."
        
        # Check 4: Detect harmful content
        has_harmful, harm_type = self._detect_harmful_content(user_input)
        if has_harmful:
            return False, self._get_safety_message(harm_type)
        
        # Check 5: Check for blocked topics
        has_blocked, topic = self._check_blocked_topics(user_input)
        if has_blocked:
            return False, f"⚠️ I cannot provide information about {topic}. Please ask about company policies, roles, or general information."
        
        return True, ""
    
    def validate_response(self, response: str) -> Tuple[bool, str]:
        """
        Validate AI response before showing to user
        
        Args:
            response: AI-generated response
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        
        # Check for personal information in response
        has_personal_info, info_type = self._detect_personal_info(response)
        if has_personal_info:
            return False, f"Response contains {info_type}"
        
        # Check response length
        if len(response) < 10:
            return False, "Response too short"
        
        return True, ""
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        current_time = datetime.now()
        
        # Initialize user history if not exists
        if user_id not in self.user_request_history:
            self.user_request_history[user_id] = []
        
        # Remove old requests (older than 1 minute)
        self.user_request_history[user_id] = [
            timestamp for timestamp in self.user_request_history[user_id]
            if current_time - timestamp < timedelta(minutes=1)
        ]
        
        # Check if under limit
        if len(self.user_request_history[user_id]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.user_request_history[user_id].append(current_time)
        return True
    
    def _detect_personal_info(self, text: str) -> Tuple[bool, str]:
        """Detect personal information in text"""
        
        patterns = {
            "Social Security Number": r'\b\d{3}-\d{2}-\d{4}\b',
            "Credit Card": r'\b\d{16}\b',
            "Phone Number": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "Email Address": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        }
        
        for info_type, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return True, info_type
        
        return False, ""
    
    def _detect_harmful_content(self, text: str) -> Tuple[bool, str]:
        """Detect potentially harmful content"""
        
        harmful_keywords = {
            "self-harm": ["suicide", "kill myself", "end my life", "hurt myself"],
            "illegal activity": ["hack", "steal", "illegal", "break into", "exploit system"],
            "violence": ["harm others", "attack", "violent"],
        }
        
        text_lower = text.lower()
        
        for harm_type, keywords in harmful_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True, harm_type
        
        return False, ""
    
    def _check_blocked_topics(self, text: str) -> Tuple[bool, str]:
        """Check if query is about blocked topics"""
        
        text_lower = text.lower()
        
        blocked_keywords = {
            "medical advice": ["diagnose", "medication", "treatment", "cure"],
            "legal advice": ["lawsuit", "legal case", "court"],
            "financial advice": ["invest in", "stock tip", "financial advice"],
            "hacking": ["bypass security", "hack into", "exploit vulnerability"],
        }
        
        for topic, keywords in blocked_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True, topic
        
        return False, ""
    
    def _get_safety_message(self, harm_type: str) -> str:
        """Get appropriate safety message based on harm type"""
        
        safety_messages = {
            "self-harm": """
⚠️ I'm concerned about your wellbeing. If you're having thoughts of self-harm, please reach out for help:
- National Suicide Prevention Lifeline: 988 or 1-800-273-8255
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

I'm here to help with work-related questions about our company.
            """.strip(),
            "illegal activity": "⚠️ I cannot provide assistance with illegal activities. Please ask about company policies, roles, or general information.",
            "violence": "⚠️ I cannot provide information that could lead to harm. Please ask appropriate questions about our company.",
        }
        
        return safety_messages.get(harm_type, "⚠️ This topic is not appropriate. Please ask about company-related topics.")
    
    def sanitize_output(self, text: str) -> str:
        """Sanitize output by removing/masking sensitive information"""
        
        # Mask SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX', text)
        
        # Mask credit card
        text = re.sub(r'\b\d{16}\b', 'XXXX-XXXX-XXXX-XXXX', text)
        
        # Mask phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'XXX-XXX-XXXX', text)
        
        return text
    
    def log_violation(self, user_id: int, violation_type: str, content: str):
        """Log policy violations for monitoring"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"⚠️ [GUARDRAIL VIOLATION] {timestamp}")
        print(f"   User ID: {user_id}")
        print(f"   Type: {violation_type}")
        print(f"   Content: {content[:100]}...")
        
        # In production, this would write to a log file or database


class InputValidator:
    """Additional input validation and sanitization"""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        return text.strip()
    
    @staticmethod
    def validate_question_format(text: str) -> Tuple[bool, str]:
        """Validate that input is a proper question or statement"""
        
        # Check for gibberish (too many special characters)
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
        if special_char_ratio > 0.3:
            return False, "⚠️ Your message contains too many special characters. Please rephrase."
        
        # Check for repeated characters (spam detection)
        if re.search(r'(.)\1{5,}', text):
            return False, "⚠️ Please remove repeated characters and try again."
        
        return True, ""
    
    @staticmethod
    def detect_prompt_injection(text: str) -> bool:
        """Detect potential prompt injection attempts"""
        
        injection_patterns = [
            r'ignore previous instructions',
            r'disregard all previous',
            r'you are now',
            r'system prompt',
            r'forget everything',
            r'new instructions',
        ]
        
        text_lower = text.lower()
        
        for pattern in injection_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False


class ResponseGuardrails:
    """Guardrails for AI responses"""
    
    @staticmethod
    def validate_response_quality(response: str, question: str) -> Tuple[bool, str]:
        """Validate that response is relevant and helpful"""
        
        # Check minimum length
        if len(response) < 20:
            return False, "Response too short"
        
        # Check if response is just repeating the question
        if question.lower() in response.lower() and len(response) < 100:
            return False, "Response just repeats question"
        
        # Check for generic unhelpful responses
        unhelpful_phrases = [
            "I don't know",
            "I cannot help",
            "I'm not sure",
        ]
        
        if any(phrase in response for phrase in unhelpful_phrases) and len(response) < 50:
            return False, "Response not helpful"
        
        return True, ""
    
    @staticmethod
    def ensure_professional_tone(response: str) -> bool:
        """Ensure response maintains professional tone"""
        
        # Check for unprofessional language
        unprofessional = [
            "dude", "bro", "yo", "lol", "lmao",
            "wtf", "omg", "bruh"
        ]
        
        response_lower = response.lower()
        
        for word in unprofessional:
            if word in response_lower:
                return False
        
        return True


# Convenience function for easy integration
def create_guardrails() -> ContentGuardrails:
    """Create and return guardrails instance"""
    return ContentGuardrails()