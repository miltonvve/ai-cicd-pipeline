#!/usr/bin/env python3
"""
AI-powered deployment decision engine
"""
import os
import json
import subprocess
import openai
from datetime import datetime, timedelta

class AIDeploymentEngine:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.risk_factors = {}
        self.deployment_history = self.load_deployment_history()

    def load_deployment_history(self):
        """Load previous deployment history for pattern analysis"""
        try:
            with open('deployment-history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"deployments": []}

    def analyze_code_complexity(self):
        """Analyze code complexity changes"""
        try:
            # Get changed files and their complexity
            changed_files = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD~1'], text=True).strip().split('\n')
            
            complexity_score = 0
            for file_path in changed_files:
                if file_path.endswith('.py'):
                    # Simple complexity analysis for Python files
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            # Count control structures as complexity indicators
                            complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'except:', 'class ', 'def ']
                            complexity_score += sum(content.count(indicator) for indicator in complexity_indicators)
                    except:
                        pass
                elif file_path.endswith(('.js', '.ts')):
                    # Simple complexity analysis for JavaScript/TypeScript
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            complexity_indicators = ['if (', 'for (', 'while (', 'function ', 'class ', '=>', 'try {']
                            complexity_score += sum(content.count(indicator) for indicator in complexity_indicators)
                    except:
                        pass
            
            # Normalize complexity score (0-1 scale)
            normalized_score = min(complexity_score / 100, 1.0)
            return normalized_score
            
        except Exception as e:
            print(f"Error analyzing code complexity: {e}")
            return 0.5  # Default moderate complexity

    def check_dependency_changes(self):
        """Check for dependency updates and their risk"""
        try:
            diff = subprocess.check_output(['git', 'diff', 'HEAD~1'], text=True)
            
            # Check for package.json, requirements.txt, etc. changes
            high_risk_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml']
            dependency_risk = 0
            
            for file_name in high_risk_files:
                if file_name in diff:
                    dependency_risk += 0.3
            
            # Check for major version updates
            if any(keyword in diff for keyword in ['"^', '~', '>=', '.*']):
                dependency_risk += 0.2
            
            return min(dependency_risk, 1.0)
            
        except Exception as e:
            print(f"Error checking dependency changes: {e}")
            return 0.0

    def evaluate_test_coverage(self):
        """Evaluate test coverage and quality"""
        try:
            # Check if tests were added/modified
            changed_files = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD~1'], text=True)
            
            test_files = [f for f in changed_files.split('\n') if 'test' in f.lower() or 'spec' in f.lower()]
            source_files = [f for f in changed_files.split('\n') if not ('test' in f.lower() or 'spec' in f.lower()) and f.endswith(('.py', '.js', '.ts'))]
            
            if not source_files:
                return 0.0  # No source changes
            
            test_coverage_ratio = len(test_files) / len(source_files) if source_files else 1.0
            
            # Risk is inverse of coverage (more tests = less risk)
            risk = max(0, 1.0 - test_coverage_ratio)
            return risk
            
        except Exception as e:
            print(f"Error evaluating test coverage: {e}")
            return 0.5

    def assess_performance_impact(self):
        """Assess potential performance impact"""
        try:
            diff = subprocess.check_output(['git', 'diff', 'HEAD~1'], text=True)
            
            # Look for performance-related changes
            performance_keywords = [
                'database', 'query', 'loop', 'recursive', 'async', 'await',
                'promise', 'timeout', 'cache', 'memory', 'cpu', 'optimization'
            ]
            
            performance_impact = 0
            for keyword in performance_keywords:
                if keyword.lower() in diff.lower():
                    performance_impact += 0.1
            
            # Check for large file changes
            lines_changed = len([line for line in diff.split('\n') if line.startswith('+') or line.startswith('-')])
            if lines_changed > 500:
                performance_impact += 0.3
            elif lines_changed > 200:
                performance_impact += 0.2
            
            return min(performance_impact, 1.0)
            
        except Exception as e:
            print(f"Error assessing performance impact: {e}")
            return 0.0

    def analyze_deployment_history(self):
        """Analyze historical deployment patterns"""
        recent_deployments = [
            d for d in self.deployment_history.get('deployments', [])
            if datetime.fromisoformat(d['timestamp']) > datetime.now() - timedelta(days=7)
        ]
        
        if not recent_deployments:
            return 0.0
        
        # Calculate failure rate in recent deployments
        failures = [d for d in recent_deployments if d.get('status') == 'failed']
        failure_rate = len(failures) / len(recent_deployments)
        
        return failure_rate

    def get_ai_risk_assessment(self, risk_factors):
        """Use AI to provide overall risk assessment"""
        prompt = f"""
        You are a DevOps expert analyzing deployment risk. Based on these risk factors, provide a comprehensive risk assessment:
        
        Risk Factors:
        - Code Complexity: {risk_factors['code_complexity']:.2f} (0=simple, 1=very complex)
        - Dependency Changes: {risk_factors['dependency_changes']:.2f} (0=none, 1=major changes)
        - Test Coverage Risk: {risk_factors['test_coverage']:.2f} (0=well tested, 1=poor coverage)
        - Performance Impact: {risk_factors['performance_impact']:.2f} (0=no impact, 1=high impact)
        - Historical Failure Rate: {risk_factors['historical_failures']:.2f} (0=no failures, 1=frequent failures)
        
        Provide your assessment in JSON format:
        {{
            "overall_risk_score": <0.0-1.0>,
            "risk_level": "<low|medium|high>",
            "recommended_strategy": "<blue_green|canary|manual_approval>",
            "key_concerns": ["concern1", "concern2"],
            "mitigation_steps": ["step1", "step2"],
            "confidence": <0.0-1.0>
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert DevOps engineer specializing in deployment risk assessment and mitigation strategies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                content = content[json_start:json_end]
            elif '{' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                content = content[json_start:json_end]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"AI assessment failed: {e}")
            # Fallback to rule-based assessment
            overall_risk = sum(risk_factors.values()) / len(risk_factors)
            if overall_risk < 0.3:
                strategy = "blue_green"
                risk_level = "low"
            elif overall_risk < 0.7:
                strategy = "canary"
                risk_level = "medium"
            else:
                strategy = "manual_approval"
                risk_level = "high"
            
            return {
                "overall_risk_score": overall_risk,
                "risk_level": risk_level,
                "recommended_strategy": strategy,
                "key_concerns": ["AI analysis unavailable"],
                "mitigation_steps": ["Manual review recommended"],
                "confidence": 0.5
            }

    def calculate_risk_score(self):
        """Calculate overall deployment risk score"""
        print("🔍 Analyzing deployment risk factors...")
        
        # Collect all risk factors
        self.risk_factors = {
            'code_complexity': self.analyze_code_complexity(),
            'dependency_changes': self.check_dependency_changes(),
            'test_coverage': self.evaluate_test_coverage(),
            'performance_impact': self.assess_performance_impact(),
            'historical_failures': self.analyze_deployment_history()
        }
        
        print("Risk factors calculated:")
        for factor, score in self.risk_factors.items():
            print(f"  {factor}: {score:.2f}")
        
        # Get AI assessment
        ai_assessment = self.get_ai_risk_assessment(self.risk_factors)
        
        return ai_assessment

    def recommend_deployment_strategy(self, assessment):
        """Recommend deployment strategy based on assessment"""
        strategy = assessment['recommended_strategy']
        
        print(f"\n🎯 Deployment Recommendation:")
        print(f"Strategy: {strategy.upper()}")
        print(f"Risk Level: {assessment['risk_level'].upper()}")
        print(f"Confidence: {assessment['confidence']:.0%}")
        
        if assessment['key_concerns']:
            print(f"Key Concerns:")
            for concern in assessment['key_concerns']:
                print(f"  - {concern}")
        
        if assessment['mitigation_steps']:
            print(f"Mitigation Steps:")
            for step in assessment['mitigation_steps']:
                print(f"  - {step}")
        
        return strategy

    def save_deployment_record(self, assessment):
        """Save deployment decision for future analysis"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'risk_score': assessment['overall_risk_score'],
            'strategy': assessment['recommended_strategy'],
            'risk_factors': self.risk_factors,
            'assessment': assessment
        }
        
        self.deployment_history['deployments'].append(record)
        
        # Keep only last 50 deployments
        if len(self.deployment_history['deployments']) > 50:
            self.deployment_history['deployments'] = self.deployment_history['deployments'][-50:]
        
        with open('deployment-history.json', 'w') as f:
            json.dump(self.deployment_history, f, indent=2)

    def run_analysis(self):
        """Main analysis execution"""
        print("🚀 AI Deployment Decision Engine")
        print("=" * 40)
        
        assessment = self.calculate_risk_score()
        strategy = self.recommend_deployment_strategy(assessment)
        
        # Save results for GitHub Actions
        with open('deployment-strategy.txt', 'w') as f:
            f.write(strategy)
        
        with open('risk-score.txt', 'w') as f:
            f.write(str(assessment['overall_risk_score']))
        
        with open('deployment-assessment.json', 'w') as f:
            json.dump(assessment, f, indent=2)
        
        # Save deployment record
        self.save_deployment_record(assessment)
        
        print(f"\n✅ Analysis complete. Strategy: {strategy}")
        return strategy, assessment

def main():
    engine = AIDeploymentEngine()
    strategy, assessment = engine.run_analysis()
    
    # Set GitHub Actions outputs
    print(f"::set-output name=deployment-strategy::{strategy}")
    print(f"::set-output name=risk-score::{assessment['overall_risk_score']}")
    print(f"::set-output name=risk-level::{assessment['risk_level']}")

if __name__ == "__main__":
    main()