import json
import dspy
from pathlib import Path
from dotenv import load_dotenv
import os

class SignificanceChecker(dspy.Signature):
    """Check if text contains explicit significance test results with clear 
    outcomes
    
    Outputs:
    - significance_result: significance test outcome
        - true: explicitly mentions significant test results (e.g. p<0.05, 
        significant difference)
        - false: explicitly mentions non-significant test results (e.g. p>0.
        05, no significant difference)
        - null: no clear significance test results mentioned, or results 
        are ambiguous/unclear
    """
    context = dspy.InputField()
    significance_result = dspy.OutputField(desc="significance test outcome (true:significant/false:not significant/null:unclear or not mentioned)")


class SignificanceJudge:
    """A class to judge significance test results in academic papers.
    
    This class processes text excerpts from academic papers and determines whether
    they contain significant or non-significant test results.
    
    Attributes:
        checker: A dspy.Predict instance for significance checking.
    """
    
    def __init__(self, model, api_key=None):
        """Initializes the SignificanceJudge with an API key.
        
        Args:
            api_key: Optional; string API key for the language model.
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
        lm = dspy.LM(api_key=api_key, model=model)
        dspy.settings.configure(lm=lm)
            
        self.checker = dspy.Predict(SignificanceChecker)
        
    def judge_content(self, input_file, output_file):
        """Processes and judges significance in content from input file.
        
        Args:
            input_file: String path to the input JSON file.
            output_file: String path for the output JSON file.
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Read {len(data['matches'])} context entries")
        
        grouped_contexts = self._group_contexts(data['matches'])
        results = self._process_contexts(grouped_contexts)
        self._save_results(results, output_file)
        
    def _group_contexts(self, matches):
        """Groups context entries by their source file.
        
        Args:
            matches: List of dictionaries containing match information.
            
        Returns:
            Dictionary mapping file names to lists of contexts.
        """
        grouped = {}
        for match in matches:
            file_name = match['file_name']
            if file_name not in grouped:
                grouped[file_name] = []
            grouped[file_name].append(match['context'])
        return grouped
        
    def _process_contexts(self, grouped_contexts):
        """Processes grouped contexts to determine significance.
        
        Args:
            grouped_contexts: Dictionary mapping file names to context lists.
            
        Returns:
            List of dictionaries containing significance judgments.
        """
        results = []
        for file_name, contexts in grouped_contexts.items():
            combined_context = self._combine_contexts(contexts)
            pred = self.checker(context=combined_context)
            
            if pred.significance_result in ['true', 'false']:
                results.append({
                    "file_name": file_name,
                    "context_count": len(contexts),
                    "is_significant": pred.significance_result == 'true'
                })
        return results
        
    def _combine_contexts(self, contexts):
        """Combines multiple contexts from the same paper.
        
        Args:
            contexts: List of context strings from the same paper.
            
        Returns:
            String containing all contexts formatted as paragraphs.
        """
        combined = f"The following are {len(contexts)} excerpted paragraphs from one paper:\n\n"
        for i, ctx in enumerate(contexts, 1):
            combined += f"Paragraph {i}:\n{ctx}\n\n"
        return combined
        
    def _save_results(self, results, output_file):
        """Saves judgment results to a JSON file.
        
        Args:
            results: List of dictionaries containing significance judgments.
            output_file: String path for the output file.
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"significance_results": results}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "related_content.json"
    output_file = "significance_results.json"
    judge = SignificanceJudge()
    judge.judge_content(input_file, output_file)
