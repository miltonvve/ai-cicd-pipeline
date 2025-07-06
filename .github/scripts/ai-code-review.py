#!/usr/bin/env python3
"""
AI-powered code review script for GitHub Actions
"""
import os
import subprocess
import openai
import json
from datetime import datetime

class AICodeReviewer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.review_results = {
            'timestamp': datetime.now().isoformat(),
            'reviews': [],
            'overall_score': 0,
            'recommendations': []
        }

    def get_git_diff(self):
        """Get the git diff for the current changes"""
        try:
            diff = subprocess.check_output(['git', 'diff', 'HEAD~1'], text=True)
            return diff
        except subprocess.CalledProcessError:
            return ""

    def get_changed_files(self):
        """Get list of changed files"""
        try:
            files = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD~1'], text=True)
            return files.strip().split('\n') if files.strip() else []
        except subprocess.CalledProcessError:
            return []

    def analyze_code_with_ai(self, diff, file_path=""):
        """Analyze code changes using OpenAI"""
        prompt = f"""
        You are a senior software engineer performing a code review for a GenAI project.
        
        File: {file_path}
        
        Analyze this git diff and provide structured feedback:
        
        1. **Code Quality** (1-10): Rate the overall code quality
        2. **Security Issues**: List any security concerns
        3. **Performance**: Identify potential performance issues
        4. **Best Practices**: Check adherence to coding standards
        5. **Bugs**: Identify potential bugs or logic errors
        6. **Recommendations**: Provide specific improvement suggestions
        
        Provide response in JSON format:
        {{
            "quality_score": <1-10>,
            "security_issues": ["issue1", "issue2"],
            "performance_issues": ["issue1", "issue2"],
            "best_practices": ["suggestion1", "suggestion2"],
            "potential_bugs": ["bug1", "bug2"],
            "recommendations": ["rec1", "rec2"],
            "overall_assessment": "summary"
        }}
        
        Code diff:
        {diff}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer specializing in AI/ML projects, security, and performance optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            # Try to extract JSON from the response
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
            return {
                "quality_score": 5,
                "security_issues": [],
                "performance_issues": [],
                "best_practices": [],
                "potential_bugs": [],
                "recommendations": [f"AI analysis failed: {str(e)}"],
                "overall_assessment": f"Analysis error: {str(e)}"
            }

    def analyze_file_specific(self, file_path):
        """Analyze specific file types with tailored prompts"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.py':
            return self.analyze_python_file(file_path)
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            return self.analyze_javascript_file(file_path)
        elif file_ext in ['.yml', '.yaml']:
            return self.analyze_yaml_file(file_path)
        elif file_ext == '.dockerfile' or 'dockerfile' in file_path.lower():
            return self.analyze_dockerfile(file_path)
        else:
            return None

    def analyze_python_file(self, file_path):
        """Python-specific analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except:
            return None
            
        prompt = f"""
        Analyze this Python code for:
        1. PEP 8 compliance
        2. Security vulnerabilities (SQL injection, code injection, etc.)
        3. Performance optimizations
        4. Error handling
        5. Type hints usage
        6. Documentation quality
        
        Code:
        {content}
        """
        
        return self.get_ai_analysis(prompt, "Python code analysis")

    def analyze_javascript_file(self, file_path):
        """JavaScript/TypeScript-specific analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except:
            return None
            
        prompt = f"""
        Analyze this JavaScript/TypeScript code for:
        1. ESLint compliance
        2. Security issues (XSS, CSRF, etc.)
        3. Performance optimizations
        4. Modern JS/TS practices
        5. Error handling
        6. Bundle size considerations
        
        Code:
        {content}
        """
        
        return self.get_ai_analysis(prompt, "JavaScript/TypeScript analysis")

    def analyze_yaml_file(self, file_path):
        """YAML configuration analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except:
            return None
            
        prompt = f"""
        Analyze this YAML configuration for:
        1. Syntax correctness
        2. Security best practices
        3. Resource allocation
        4. Environment-specific configurations
        5. Secrets management
        
        YAML:
        {content}
        """
        
        return self.get_ai_analysis(prompt, "YAML configuration analysis")

    def analyze_dockerfile(self, file_path):
        """Dockerfile-specific analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except:
            return None
            
        prompt = f"""
        Analyze this Dockerfile for:
        1. Security best practices
        2. Image size optimization
        3. Layer caching efficiency
        4. Vulnerability scanning
        5. Multi-stage build usage
        
        Dockerfile:
        {content}
        """
        
        return self.get_ai_analysis(prompt, "Dockerfile analysis")

    def get_ai_analysis(self, prompt, analysis_type):
        """Generic AI analysis method"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are an expert in {analysis_type} for DevOps and AI/ML projects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def generate_summary_report(self):
        """Generate overall summary report"""
        if not self.review_results['reviews']:
            return "No code changes to review."
        
        total_score = sum(review.get('quality_score', 5) for review in self.review_results['reviews'])
        avg_score = total_score / len(self.review_results['reviews'])
        self.review_results['overall_score'] = avg_score
        
        # Collect all issues
        all_security_issues = []
        all_performance_issues = []
        all_recommendations = []
        
        for review in self.review_results['reviews']:
            all_security_issues.extend(review.get('security_issues', []))
            all_performance_issues.extend(review.get('performance_issues', []))
            all_recommendations.extend(review.get('recommendations', []))
        
        summary = f"""
# AI Code Review Summary

## Overall Quality Score: {avg_score:.1f}/10

## Files Reviewed: {len(self.review_results['reviews'])}

## Critical Issues Found:
### Security Issues: {len(all_security_issues)}
{chr(10).join(f"- {issue}" for issue in all_security_issues[:5])}

### Performance Issues: {len(all_performance_issues)}
{chr(10).join(f"- {issue}" for issue in all_performance_issues[:5])}

## Top Recommendations:
{chr(10).join(f"- {rec}" for rec in all_recommendations[:10])}

## Deployment Recommendation:
{"✅ APPROVED - Low risk changes" if avg_score >= 7 else "⚠️ REVIEW NEEDED - Medium risk changes" if avg_score >= 5 else "❌ BLOCKED - High risk changes"}
        """
        
        return summary

    def run_review(self):
        """Main review execution"""
        print("🤖 Starting AI code review...")
        
        diff = self.get_git_diff()
        changed_files = self.get_changed_files()
        
        if not diff and not changed_files:
            print("No changes detected.")
            return
        
        # Analyze overall diff
        if diff:
            print("Analyzing overall changes...")
            overall_analysis = self.analyze_code_with_ai(diff)
            self.review_results['reviews'].append(overall_analysis)
        
        # Analyze individual files
        for file_path in changed_files:
            if os.path.exists(file_path):
                print(f"Analyzing {file_path}...")
                file_analysis = self.analyze_file_specific(file_path)
                if file_analysis:
                    self.review_results['reviews'].append({
                        'file': file_path,
                        'analysis': file_analysis
                    })
        
        # Generate and display summary
        summary = self.generate_summary_report()
        
        print("\n" + "="*60)
        print("AI CODE REVIEW RESULTS")
        print("="*60)
        print(summary)
        print("="*60)
        
        # Save results for later use
        with open('ai-review-results.json', 'w') as f:
            json.dump(self.review_results, f, indent=2)
        
        # Save summary for GitHub Actions
        with open('review-summary.md', 'w') as f:
            f.write(summary)
        
        # Set GitHub Actions output
        print(f"::set-output name=quality-score::{self.review_results['overall_score']}")
        print(f"::set-output name=review-status::{'approved' if self.review_results['overall_score'] >= 7 else 'needs-review' if self.review_results['overall_score'] >= 5 else 'blocked'}")

def main():
    reviewer = AICodeReviewer()
    reviewer.run_review()

if __name__ == "__main__":
    main()