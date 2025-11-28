import openai
from config import Config
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def analyze_performance_gaps(self, metrics: Dict[str, float], domain: str) -> List[str]:
        """Analyze metrics to identify performance gaps"""
        prompt = f"""
        As a business AI analyst, analyze these {domain} metrics and identify the top 3 performance gaps:
        
        Metrics: {metrics}
        
        Return ONLY a JSON array of gap descriptions, no other text.
        Example: ["High response time affecting customer satisfaction", "Low resolution rate for technical issues"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.BASE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            gaps = eval(response.choices[0].message.content)
            return gaps[:3]  # Return top 3 gaps
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return ["Error in analysis - using fallback rules"]
    
    def generate_improvement_plan(self, gaps: List[str], domain: str) -> Dict[str, Any]:
        """Generate specific improvement proposals"""
        prompt = f"""
        For {domain} business, generate specific improvement proposals for these gaps: {gaps}
        
        Return JSON: {{"proposals": [{{"hypothesis": "text", "intervention": "prompt_change|adapter_training", "expected_impact": 0.15}}]}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.BASE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            return eval(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Proposal generation failed: {e}")
            return {"proposals": []}
    
    def test_intervention(self, hypothesis: str, test_data: List[str]) -> Dict[str, Any]:
        """Test a specific intervention with sample data"""
        prompt = f"""
        Test this business hypothesis: {hypothesis}
        
        With sample conversations: {test_data}
        
        Return JSON: {{"success_rate": 0.85, "improvement": 0.12, "risks": ["risk1", "risk2"]}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.BASE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            return eval(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Intervention test failed: {e}")
            return {"success_rate": 0.0, "improvement": 0.0, "risks": ["Test failed"]}