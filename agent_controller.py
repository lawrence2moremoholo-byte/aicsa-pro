from services.ai_service import AIService
from infrastructure.database import SessionLocal, Experiment, PerformanceMetrics
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class AgentController:
    def __init__(self):
        self.ai_service = AIService()
        self.db = SessionLocal()
    
    def analyze_client_performance(self, client_id: int, domain: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Main RSI cycle for a client"""
        
        # 1. Analyze gaps
        gaps = self.ai_service.analyze_performance_gaps(metrics, domain)
        print(f"Identified gaps for client {client_id}: {gaps}")
        
        # 2. Generate proposals
        proposals_data = self.ai_service.generate_improvement_plan(gaps, domain)
        
        # 3. Test top proposal
        tested_proposals = []
        for proposal in proposals_data.get("proposals", [])[:2]:  # Test top 2
            test_result = self.ai_service.test_intervention(
                proposal["hypothesis"], 
                self._get_test_data(domain)
            )
            
            # Save experiment
            experiment = Experiment(
                client_id=client_id,
                hypothesis=proposal["hypothesis"],
                intervention_type=proposal["intervention"],
                status="completed",
                results=json.dumps(test_result)
            )
            self.db.add(experiment)
            self.db.commit()
            
            tested_proposals.append({
                "hypothesis": proposal["hypothesis"],
                "intervention": proposal["intervention"],
                "test_results": test_result
            })
        
        # 4. Return actionable recommendations
        return {
            "client_id": client_id,
            "domain": domain,
            "performance_gaps": gaps,
            "tested_proposals": tested_proposals,
            "recommendations": self._generate_recommendations(tested_proposals)
        }
    
    def _get_test_data(self, domain: str) -> List[str]:
        """Get domain-specific test data"""
        test_data = {
            "customer_support": [
                "Customer: I can't login to my account",
                "Customer: My order hasn't arrived",
                "Customer: I want to cancel my subscription"
            ],
            "technical_support": [
                "User: The system is showing error 404",
                "User: How do I reset my password?",
                "User: The application keeps crashing"
            ]
        }
        return test_data.get(domain, [])
    
    def _generate_recommendations(self, proposals: List[Dict]) -> List[str]:
        """Generate business recommendations from test results"""
        recommendations = []
        for proposal in proposals:
            if proposal["test_results"]["success_rate"] > 0.7:
                recommendations.append(f"IMPLEMENT: {proposal['hypothesis']}")
            else:
                recommendations.append(f"REJECT: {proposal['hypothesis']} - Low success rate")
        
        return recommendations