import json

class SignificanceAnalyzer:
    """A class to analyze significance test results based on context thresholds.
    
    This class processes significance test results and provides statistical analysis
    based on different context count thresholds.
    
    Attributes:
        data: Dictionary containing the loaded significance test results.
    """
    
    def __init__(self, data_file):
        """Initializes the SignificanceAnalyzer with a data file.
        
        Args:
            data_file: String path to the JSON file containing significance results.
        """
        with open(data_file, 'r') as f:
            self.data = json.load(f)
            
    def analyze_by_threshold(self, threshold):
        """Analyzes results for a specific context count threshold.
        
        Args:
            threshold: Integer threshold for context count filtering.
            
        Returns:
            Dictionary containing analysis results including counts and percentages.
        """
        total, true_count, false_count = self._count_results(threshold)
        percentage = (true_count/total*100) if total > 0 else 0
        
        return {
            'threshold': threshold,
            'total': total,
            'true_count': true_count,
            'false_count': false_count,
            'percentage': percentage
        }
        
    def analyze_all_thresholds(self, start_threshold=2):
        """Analyzes results across all possible thresholds.
        
        Args:
            start_threshold: Optional; integer starting threshold value.
            
        Returns:
            List of dictionaries containing analysis results for each threshold.
        """
        results = []
        threshold = start_threshold
        prev_total = 0
        
        while True:
            stats = self.analyze_by_threshold(threshold)
            if stats['total'] == prev_total and stats['total'] > 0:
                break
                
            results.append(stats)
            prev_total = stats['total']
            threshold += 1
            
        return results
        
    def calculate_statistics(self, results):
        """Calculates summary statistics across all thresholds.
        
        Args:
            results: List of dictionaries containing threshold analysis results.
            
        Returns:
            Dictionary containing average percentage and variance, or None if no results.
        """
        percentages = [r['percentage'] for r in results]
        if not percentages:
            return None
            
        avg = sum(percentages) / len(percentages)
        variance = sum((x - avg) ** 2 for x in percentages) / len(percentages)
        
        return {
            'average_percentage': avg,
            'variance': variance
        }
        
    def _count_results(self, threshold):
        """Counts true and false results below a given threshold.
        
        Args:
            threshold: Integer threshold for context count filtering.
            
        Returns:
            Tuple of (total_count, true_count, false_count).
        """
        true_count = false_count = 0
        
        if isinstance(self.data, dict) and 'significance_results' in self.data:
            for result in self.data['significance_results']:
                if result['context_count'] < threshold:
                    if result['is_significant']:
                        true_count += 1
                    else:
                        false_count += 1
                        
        return true_count + false_count, true_count, false_count
