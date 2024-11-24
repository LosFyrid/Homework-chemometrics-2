from parser import PDFParser
from related_content_extractor import ContentExtractor
from judge import SignificanceJudge
from data_processer import SignificanceAnalyzer
from getter import read_excel_data, download_papers

def main(search_terms):
    """Main function to orchestrate the paper analysis pipeline.
    
    This function coordinates the entire process of analyzing academic papers:
    1. Reading paper metadata and downloading PDFs
    2. Converting PDFs to text
    3. Extracting relevant content
    4. Judging significance
    5. Analyzing results
    """
    # Read metadata and download papers
    metadata = read_excel_data("metadata.xls")
    print(f"Read {len(metadata)} records from Excel")
    
    metadata_with_pdfs = download_papers(metadata, "downloaded_papers")
    metadata_with_pdfs.to_excel("metadata_with_pdfs.xlsx", index=False)
    
    # Initialize and run PDF parser
    parser = PDFParser(
        input_dir="downloaded_papers",
        output_dir="parsed_papers"
    )
    parser.parse_all_pdfs()
    
    # Extract relevant content
    extractor = ContentExtractor(
        input_dir="parsed_papers",
        output_file="related_content.json",
        context_length=300,
        loose_match_length=100
    )
    extractor.extract_content(search_terms, case_sensitive=False)
    
    # Judge significance
    judge = SignificanceJudge(model="gpt-4o")
    judge.judge_content(
        input_file="related_content.json",
        output_file="significance_results.json"
    )
    
    # Analyze results
    analyzer = SignificanceAnalyzer("significance_results.json")
    results = analyzer.analyze_all_thresholds()
    
    # Print analysis results
    for result in results:
        print(f"\nFor threshold {result['threshold']}:")
        print(f"Total literature count: {result['total']}")
        print(f"True count: {result['true_count']}")
        print(f"False count: {result['false_count']}")
        print(f"True percentage: {result['percentage']:.2f}%")
    
    # Calculate and print statistics
    stats = analyzer.calculate_statistics(results)
    if stats:
        print(f"\nAverage True percentage across all thresholds: {stats['average_percentage']:.2f}%")
        print(f"Variance of True percentages: {stats['variance']:.2f}")

if __name__ == "__main__":
    search_terms = ["p-value", "statistical+significance", "significance+test"]
    main(search_terms)
