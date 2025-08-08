"""
Simple Gemini manager for handling Google Gemini API requests.
"""
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logger.info("Google Generative AI available")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available - using dummy responses")


class SimpleGeminiManager:
    """Simple Gemini manager with fallback to dummy responses."""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-pro"):
        self.api_key = api_key
        self.model_name = model
        self.model_instance = None
        self.max_tokens = 15000
        self.temperature = 0.1
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model."""
        if not GEMINI_AVAILABLE:
            logger.warning("Google Generative AI not available - using dummy responses")
            return
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("No valid Gemini API key provided - using dummy responses")
            return
        
        try:
            logger.info(f"Initializing Gemini model: {self.model_name}")
            genai.configure(api_key=self.api_key)
            self.model_instance = genai.GenerativeModel(self.model_name)
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            logger.warning("Using dummy responses")
            self.model_instance = None
    
    def _create_prompt_for_question(self, question: str, context_chunks: list) -> str:
        """Create a prompt for answering a specific question."""
        context_text = "\n\n".join([f"Context {i+1}: {chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""You are an expert AI assistant designed to analyze insurance policies and legal documents with high accuracy.

TASK: Answer the following question based ONLY on the provided document context.

QUESTION: {question}

DOCUMENT CONTEXT:
{context_text}

INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the context above
2. If the answer cannot be found in the context, clearly state "The information is not available in the provided document"
3. Provide specific details, numbers, and quotes from the document when possible
4. Be concise but comprehensive
5. Assess your confidence level (high/medium/low) based on the available information

RESPONSE FORMAT:
Answer: [Your detailed answer here]
Confidence: [high/medium/low]
Supporting Evidence: [List key points or quotes from the document that support your answer]

Please provide your response:"""
        
        return prompt
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API."""
        if self.model_instance is None:
            return self._generate_dummy_response(prompt)
        
        try:
            logger.info("Generating response with Gemini API")
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=0.9
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini API")
                return "I apologize, but I couldn't generate a response for this query."
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return self._generate_dummy_response(prompt)
    
    def _generate_dummy_response(self, prompt: str) -> str:
        """Generate a dummy response when Gemini is not available."""
        # Extract question from prompt if possible
        if "QUESTION:" in prompt:
            question_start = prompt.find("QUESTION:") + 9
            question_end = prompt.find("\n", question_start)
            question = prompt[question_start:question_end].strip()
        else:
            question = "the query"
        
        return f"""Answer: I apologize, but I'm currently unable to provide a detailed answer to "{question}" because the Gemini API is not properly configured. Please ensure you have set up a valid GEMINI_API_KEY in your configuration.

Confidence: low
Supporting Evidence: No evidence available due to API configuration issue."""
    
    async def answer_question_with_context(self, question: str, context_chunks: list) -> Dict[str, Any]:
        """Answer a specific question using provided context."""
        try:
            # Create prompt for the question
            prompt = self._create_prompt_for_question(question, context_chunks)
            
            # Generate response
            response_text = await self.generate_response(prompt)
            
            # Parse the response
            return self._parse_response(response_text, question)
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {
                "question": question,
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "confidence": "low",
                "supporting_evidence": []
            }
    
    def _parse_response(self, response_text: str, question: str) -> Dict[str, Any]:
        """Parse the response text to extract answer, confidence, and evidence."""
        try:
            # Initialize default values
            answer = response_text
            confidence = "medium"
            supporting_evidence = []
            
            # Try to extract structured information
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith('answer:'):
                    current_section = 'answer'
                    answer = line[7:].strip()
                elif line.lower().startswith('confidence:'):
                    current_section = 'confidence'
                    confidence_text = line[11:].strip().lower()
                    if confidence_text in ['high', 'medium', 'low']:
                        confidence = confidence_text
                elif line.lower().startswith('supporting evidence:'):
                    current_section = 'evidence'
                    evidence_text = line[20:].strip()
                    if evidence_text:
                        supporting_evidence.append(evidence_text)
                elif current_section == 'answer' and line:
                    answer += ' ' + line
                elif current_section == 'evidence' and line:
                    supporting_evidence.append(line)
            
            return {
                "question": question,
                "answer": answer,
                "confidence": confidence,
                "supporting_evidence": supporting_evidence
            }
            
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return {
                "question": question,
                "answer": response_text,
                "confidence": "medium",
                "supporting_evidence": []
            }
    
    def test_connection(self) -> bool:
        """Test Gemini API connection."""
        if self.model_instance is None:
            return False
        
        try:
            # Simple test
            response = self.model_instance.generate_content("Test")
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False


# Global instance
_gemini_manager: Optional[SimpleGeminiManager] = None

def get_simple_gemini_manager(api_key: str = None) -> SimpleGeminiManager:
    """Get simple Gemini manager instance."""
    global _gemini_manager
    if _gemini_manager is None:
        _gemini_manager = SimpleGeminiManager(api_key=api_key)
    return _gemini_manager
