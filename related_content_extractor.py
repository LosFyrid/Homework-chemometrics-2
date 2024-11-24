import json
from pathlib import Path

class ContentExtractor:
    """A class to extract relevant content from text files based on search terms.
    
    This class implements both exact and loose matching strategies to find and
    extract content around specified search terms from text files.
    
    Attributes:
        input_dir: Path object pointing to the directory containing text files.
        output_file: Path object for the JSON output file.
        context_length: Integer specifying characters to include around matches.
        loose_match_length: Integer specifying the window size for loose matching.
        matches: List storing all matched content.
    """
    
    def __init__(self, input_dir, output_file, context_length=300, loose_match_length=100):
        """Initializes the ContentExtractor with specified parameters.
        
        Args:
            input_dir: String or Path to the directory containing text files.
            output_file: String or Path for the output JSON file.
            context_length: Optional; number of characters to include around matches.
            loose_match_length: Optional; window size for loose matching.
        """
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.context_length = context_length
        self.loose_match_length = loose_match_length
        self.matches = []
        
    def extract_content(self, search_terms, case_sensitive=True):
        """Extracts content matching the search terms from all text files.
        
        Args:
            search_terms: List of strings to search for.
            case_sensitive: Optional; boolean indicating if search is case-sensitive.
        """
        txt_files = list(self.input_dir.glob('*.txt'))
        print(f"Found {len(txt_files)} text files")
        
        for txt_file in txt_files:
            self._process_file(txt_file, search_terms, case_sensitive)
            
        self._save_results()
        
    def _process_file(self, txt_file, search_terms, case_sensitive):
        """Processes a single text file for all search terms.
        
        Args:
            txt_file: Path object of the text file to process.
            search_terms: List of strings to search for.
            case_sensitive: Boolean indicating if search is case-sensitive.
        """
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            search_content = content if case_sensitive else content.lower()
            
            for term in search_terms:
                if "+" in term:
                    self._loose_match(content, search_content, term, txt_file, case_sensitive)
                else:
                    self._exact_match(content, search_content, term, txt_file, case_sensitive)
                    
        except Exception as e:
            print(f"Error processing {txt_file.name}: {str(e)}")
            
    def _loose_match(self, content, search_content, term, txt_file, case_sensitive):
        """Performs loose matching for terms connected with '+'.
        
        Args:
            content: Original text content.
            search_content: Processed text content for searching.
            term: Search term containing multiple keywords connected by '+'.
            txt_file: Path object of the current file.
            case_sensitive: Boolean indicating if search is case-sensitive.
        """
        keywords = term.split("+")
        if not case_sensitive:
            keywords = [k.lower() for k in keywords]
            
        for i in range(len(search_content)):
            window_end = min(i + self.loose_match_length, len(search_content))
            window = search_content[i:window_end]
            
            if all(k in window for k in keywords):
                self._add_match(content, i, window_end, term, txt_file, "loose_match")
                break
                
    def _exact_match(self, content, search_content, term, txt_file, case_sensitive):
        """Performs exact matching for single terms.
        
        Args:
            content: Original text content.
            search_content: Processed text content for searching.
            term: Single search term.
            txt_file: Path object of the current file.
            case_sensitive: Boolean indicating if search is case-sensitive.
        """
        search_term = term if case_sensitive else term.lower()
        start_pos = 0
        
        while True:
            pos = search_content.find(search_term, start_pos)
            if pos == -1:
                break
                
            self._add_match(content, pos, pos + len(term), term, txt_file, "exact_match")
            start_pos = pos + len(term)
            
    def _add_match(self, content, start, end, term, txt_file, match_type):
        """Adds a match to the matches list with surrounding context.
        
        Args:
            content: Original text content.
            start: Starting position of the match.
            end: Ending position of the match.
            term: The matched search term.
            txt_file: Path object of the current file.
            match_type: String indicating the type of match ("exact_match" or "loose_match").
        """
        context_start = max(0, start - self.context_length)
        context_end = min(len(content), end + self.context_length)
        
        self.matches.append({
            "file_name": txt_file.name,
            "match_type": match_type,
            "match_term": term,
            "context": content[context_start:context_end]
        })
        
    def _save_results(self):
        """Saves all matches to the output JSON file."""
        if self.matches:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump({"matches": self.matches}, f, ensure_ascii=False, indent=2)
            print(f"\nSaved {len(self.matches)} matches to: {self.output_file}")
        else:
            print("\nNo matches found")

if __name__ == "__main__":
    # 测试代码
    input_dir = "parsed_papers"
    search_terms = ["p-value", "statistical+significance", "significance+test", ]  # 示例:既有普通搜索词也有宽松匹配词组
    output_file = "related_content.json"
    
    extractor = ContentExtractor(
        input_dir=input_dir,
        output_file=output_file,
        context_length=300,
        loose_match_length=200
    )
    extractor.extract_content(search_terms, case_sensitive=False)
