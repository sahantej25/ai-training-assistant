# src/evaluation/evaluator.py

import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List
import json

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.agents.assistant import AITrainingAssistant
from src.utils.config import config


class Evaluator:
    """Evaluate the AI Training Assistant"""
    
    def __init__(self):
        print("🔬 Initializing Evaluator...")
        self.assistant = AITrainingAssistant()
        self.eval_df = pd.read_csv(config.EVAL_SET_PATH)
        print(f"✅ Loaded {len(self.eval_df)} test questions\n")
    
    def evaluate_routing(self) -> Dict:
        """Evaluate routing accuracy"""
        print("="*70)
        print("🎯 EVALUATING ROUTING ACCURACY")
        print("="*70 + "\n")
        
        correct = 0
        total = 0
        results = []
        
        for idx, row in self.eval_df.iterrows():
            question = row['question']
            expected_route = row['expected_route']
            
            # Skip if no expected route (like direct_llm questions)
            if pd.isna(expected_route) or expected_route == '':
                continue
            
            total += 1
            
            # Get actual route
            result = self.assistant.answer(question)
            actual_route = result['route']
            
            is_correct = (actual_route == expected_route)
            if is_correct:
                correct += 1
            
            status = "✅" if is_correct else "❌"
            print(f"{status} Q{idx+1}: {question[:50]}...")
            print(f"   Expected: {expected_route} | Got: {actual_route}\n")
            
            results.append({
                'question_id': f"Q{idx+1:02d}",
                'question': question,
                'expected_route': expected_route,
                'actual_route': actual_route,
                'correct': is_correct
            })
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print("="*70)
        print(f"📊 ROUTING ACCURACY: {accuracy:.1f}% ({correct}/{total})")
        print("="*70 + "\n")
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'details': results
        }
    
    def evaluate_answer_quality(self) -> Dict:
        """Evaluate if answers contain expected information"""
        print("="*70)
        print("📝 EVALUATING ANSWER QUALITY")
        print("="*70 + "\n")
        
        results = []
        has_sources_count = 0
        relevant_count = 0
        total = 0
        
        for idx, row in self.eval_df.iterrows():
            question = row['question']
            expected_route = row['expected_route']
            gold_source = row.get('gold_source', '')
            
            # Get answer
            result = self.assistant.answer(question)
            answer = result['answer'].lower()
            sources = result.get('sources', [])
            
            # Check if should have sources
            should_have_sources = expected_route not in ['direct_llm', '']
            
            if should_have_sources:
                total += 1
                
                # Check if has sources
                has_sources = len(sources) > 0
                if has_sources:
                    has_sources_count += 1
                
                # Check if answer seems relevant (simple heuristic)
                is_relevant = len(answer) > 50  # At least some content
                if is_relevant:
                    relevant_count += 1
                
                status = "✅" if (has_sources and is_relevant) else "⚠️"
                print(f"{status} Q{idx+1}: {question[:50]}...")
                print(f"   Sources: {sources}")
                print(f"   Answer length: {len(answer)} chars\n")
                
                results.append({
                    'question_id': f"Q{idx+1:02d}",
                    'has_sources': has_sources,
                    'is_relevant': is_relevant,
                    'sources': sources,
                    'answer_preview': answer[:200]
                })
        
        citation_rate = (has_sources_count / total * 100) if total > 0 else 0
        relevance_rate = (relevant_count / total * 100) if total > 0 else 0
        
        print("="*70)
        print(f"📊 CITATION RATE: {citation_rate:.1f}% ({has_sources_count}/{total})")
        print(f"📊 RELEVANCE RATE: {relevance_rate:.1f}% ({relevant_count}/{total})")
        print("="*70 + "\n")
        
        return {
            'citation_rate': citation_rate,
            'relevance_rate': relevance_rate,
            'has_sources_count': has_sources_count,
            'relevant_count': relevant_count,
            'total': total,
            'details': results
        }
    
    def run_full_evaluation(self) -> Dict:
        """Run complete evaluation"""
        print("\n" + "🚀 STARTING FULL EVALUATION\n")
        
        # Evaluate routing
        routing_results = self.evaluate_routing()
        
        # Evaluate answer quality
        quality_results = self.evaluate_answer_quality()
        
        # Overall summary
        print("="*70)
        print("📈 FINAL EVALUATION SUMMARY")
        print("="*70)
        print(f"✅ Routing Accuracy:  {routing_results['accuracy']:.1f}%")
        print(f"📚 Citation Rate:     {quality_results['citation_rate']:.1f}%")
        print(f"📝 Relevance Rate:    {quality_results['relevance_rate']:.1f}%")
        print("="*70 + "\n")
        
        # Save results
        results = {
            'routing': routing_results,
            'quality': quality_results,
            'summary': {
                'routing_accuracy': routing_results['accuracy'],
                'citation_rate': quality_results['citation_rate'],
                'relevance_rate': quality_results['relevance_rate']
            }
        }
        
        # Save to file
        output_file = "evaluation_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}\n")
        
        return results


def main():
    evaluator = Evaluator()
    results = evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()