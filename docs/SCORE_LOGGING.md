# Score Logging Documentation

## Overview
The updated search service now includes comprehensive logging to track similarity scores and relevance metrics throughout the RAG pipeline.

## Log Levels and What They Show

### INFO Level Logs
- **Search Query Start**: Shows the query and top_k parameter
- **Search Results Summary**: Average distance, similarity scores, best/worst matches
- **Relevance Score Calculation**: Overall relevance score and individual scores per source
- **RAG Pipeline Completion**: Final success status and overall metrics
- **Search Quality Analysis**: Quality assessment (Excellent/Good/Fair/Poor) based on similarity scores

### DEBUG Level Logs
- **Individual Result Details**: Distance and similarity score for each search result
- **Detailed score breakdowns**: Per-document scoring information

## Example Log Output

```
2025-06-12 10:30:15 - app.services.search_service - INFO - Search Query: 'artificial intelligence' | Top K: 3

2025-06-12 10:30:15 - app.services.search_service - DEBUG - Result 1: ai_ml_guide.txt (chunk 1) | Distance: 0.1250 | Similarity: 0.8750
2025-06-12 10:30:15 - app.services.search_service - DEBUG - Result 2: ai_ml_guide.txt (chunk 3) | Distance: 0.2100 | Similarity: 0.7900
2025-06-12 10:30:15 - app.services.search_service - DEBUG - Result 3: document2.pdf (chunk 1) | Distance: 0.3200 | Similarity: 0.6800

2025-06-12 10:30:15 - app.services.search_service - INFO - Search Results Summary - Found: 3 | Avg Distance: 0.2183 | Avg Similarity: 0.7817 | Best Match Distance: 0.1250 | Worst Match Distance: 0.3200

2025-06-12 10:30:15 - app.services.search_service - INFO - Search Quality Analysis - Quality: Good | Avg Similarity: 0.7817 | Best Match: 0.8750 | Worst Match: 0.6800

2025-06-12 10:30:16 - app.services.search_service - INFO - Relevance Score Calculation - Overall Score: 0.7245 | Individual Scores: ['0.8889', '0.8261', '0.7576'] | Sources Used: 3

2025-06-12 10:30:17 - app.services.search_service - INFO - RAG Chat Pipeline Completed - Success: True | Final Relevance Score: 0.7245 | Sources Found: 3 | Model Used: gpt-4o
```

## Score Metrics Explained

### Distance vs Similarity
- **Distance**: Cosine distance (0 = identical, 1 = completely different)
- **Similarity**: 1 - distance (1 = identical, 0 = completely different)

### Relevance Score
- Calculated as: `average(1 / (1 + distance))` for all sources
- Range: 0.0 to 1.0
- Higher values indicate better relevance

### Quality Assessment
- **Excellent**: Average similarity ≥ 0.8
- **Good**: Average similarity ≥ 0.6
- **Fair**: Average similarity ≥ 0.4  
- **Poor**: Average similarity < 0.4

## Configuration

### Environment Variables
```bash
# Logging configuration
LOG_LEVEL=DEBUG          # Set to DEBUG for detailed logs, INFO for standard logs
ENABLE_FILE_LOGGING=true # Enable/disable file logging
LOG_FILE=app.log         # Log file path
```

### Log File Rotation
- Maximum file size: 10MB
- Backup files: 5
- Old files are automatically archived

## Usage Tips

1. **Monitor Search Quality**: Watch the "Search Quality Analysis" logs to identify when search results are poor
2. **Track Performance**: Use relevance scores to monitor RAG system performance over time
3. **Debug Issues**: Enable DEBUG level logging to see individual result scores
4. **Production Monitoring**: Use INFO level logs in production to avoid log spam

## Testing

Run the test script to see the logging in action:
```bash
python test_logging.py
```

This will perform a sample search and demonstrate all the logging features.
