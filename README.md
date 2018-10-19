# line-segmentation-gcp-vision
Google Cloud Vision OCR return results per line

Ported from JavaScript: 
https://github.com/sshniro/line-segmentation-algorithm-to-gcp-vision/

Google vision outperforms most of the ocr providers. It provides two options for OCR capabilities.

- TEXT_DETECTION - Word output with coordinates
- DOCUMENT_TEXT_DETECTION - OCR on dense text to extract lines and paragraph information

The second option is good for data extraction from normal articles but for content like invoice and receipts if the distance is too far apart the google vision identifies them as seperate paragraphs. The below images shows the sample output for a typical invoice from google vision.
