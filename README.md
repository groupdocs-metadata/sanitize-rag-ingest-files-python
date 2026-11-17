# RAG Ingest Metadata Sanitization

[![Docs](https://img.shields.io/badge/Docs-2865E0?style=for-the-badge&logo=Hugo&logoColor=white)](https://docs.groupdocs.com/metadata/python-net/)
[![Blog](https://img.shields.io/badge/Blog-2865E0?style=for-the-badge&logo=WordPress&logoColor=white)](https://blog.groupdocs.com/categories/groupdocs.metadata-product-family/)
[![Free Support](https://img.shields.io/badge/Free%20Support-2865E0?style=for-the-badge&logo=Discourse&logoColor=white)](https://forum.groupdocs.com/c/metadata/)
[![Temporary License](https://img.shields.io/badge/Temporary%20License-2865E0?style=for-the-badge&logo=rocket&logoColor=white)](https://purchase.groupdocs.com/temp-license/100216)

## Overview

`sanitize-rag-ingest-files-python` is a runnable Python demo that inspects inbound file metadata, strips it with `sanitize()`, and re-opens the cleaned copy before the bytes reach a vector store or LLM. It uses GroupDocs.Metadata for Python via .NET 26.9.0 across DOCX, PDF, and JPEG inputs. The sample targets engineers wiring a privacy gate into RAG ingest or agent toolchains.

I put this together after watching an ingest job embed Author, EXIF GPS, and XMP creator fields that never belonged in the retrieval index.

## Technology Stack

- Platform: Python 3.13 (via .NET runtime bridge)
- Product: GroupDocs.Metadata for Python via .NET 26.9.0
- Language: Python
- Package: `groupdocs-metadata-net`

## Problem Statement

RAG and agent pipelines often index whatever arrives in the upload folder. Office authors, PDF Info/XMP packets, and JPEG EXIF travel with the file even when the body text is redacted elsewhere. Once those fields land in embeddings or tool traces, they are hard to unwind.

Browser cleaners and one-off desktop tools do not sit in a batch ingest path. Teams need a single API that works on mixed formats, returns a removal count, and can prove the cleaned file is quieter on a second open.

GroupDocs.Metadata for Python via .NET exposes `get_document_info()`, `find_properties()`, and `sanitize()` so the same gate can audit, clean, and verify before embedding.

## Solution Overview

GroupDocs.Metadata addresses the ingest leak through one `Metadata` object per file, a full-package `sanitize()` pass, and a re-open check. Key technical features include:

- Pre-clean audit: list format, page count, and every detected property.
- Full wipe: `sanitize()` clears recognized packages (authors, comments, EXIF, XMP, and similar).
- Mixed formats: the same three methods run on DOCX, PDF, and JPEG.
- Post-clean proof: re-open with `find_properties()` and count what remains.
- Pip installable: `groupdocs-metadata-net` 26.9.0 on Python 3.13.

## When should I use this demo?

Use this demo when files enter a RAG, LLM, or agent pipeline and must not carry Author, GPS, or XMP identity into the index. Prefer `sanitize_file_for_rag_ingest` as the final export step, always after `inspect_inbound_file_metadata` and before `verify_metadata_cleared`. Saving a cleaned file requires a license; evaluation mode can block `save()`.

## Prerequisites

Before running these examples, ensure you have:

- Runtime - Python 3.13 (`py -3.13`)
- Package - `groupdocs-metadata-net>=26.9.0` from `requirements.txt`
- License (optional for full Save) - set `REPLACE_WITH_YOUR_LICENSE_PATH` in the demo to your `.lic` file
- Sample inputs - `documents/incoming.docx`, `incoming.pdf`, `incoming.jpg`

## Getting Started

### Installation

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Optionally point `REPLACE_WITH_YOUR_LICENSE_PATH` at your GroupDocs.Metadata license.
2. Confirm the three files under `documents/` are present.
3. Run `py -3.13 sanitize_rag_ingest_demo.py`.

## Repository Structure

```
sanitize-rag-ingest-files-python/
│
├── requirements.txt
├── sanitize_rag_ingest_demo.py
├── documents/
│   ├── incoming.docx
│   ├── incoming.pdf
│   └── incoming.jpg
└── Result/
    └── Result-is-generated.txt
```

## Implementation Guide

### Method 1: Inspect inbound metadata

```python
with Metadata(input_path) as metadata:
    info = metadata.get_document_info()
    print(f"format={info.file_type.file_format}")
    print(f"pages={info.page_count}")
    print(f"encrypted={info.is_encrypted}")

    count = 0
    for prop in metadata.find_properties(lambda p: True):
        print(f"{prop.name}={prop.value}")
        count += 1
    return count
```

### Method 2: Sanitize for RAG ingest

```python
with Metadata(input_path) as metadata:
    removed = metadata.sanitize()
    metadata.save(output_path)
    return int(removed)
```

### Method 3: Verify metadata cleared

```python
with Metadata(cleaned_path) as metadata:
    remaining = 0
    for prop in metadata.find_properties(lambda p: True):
        print(f"{prop.name}={prop.value}")
        remaining += 1
    return remaining
```

## Expected Output

The demo prints a before-count per file, the number of properties removed by `sanitize()`, writes `Result/<name>-sanitized.<ext>`, then prints the remaining property count after re-open. Use the before/after counts as the ingest gate evidence.

## Keywords

sanitize metadata RAG, strip EXIF before LLM, GroupDocs.Metadata Python, clean document metadata, RAG ingest sanitize, remove XMP authors, metadata removal API, PDF DOCX JPEG sanitize

## Related Resources

- [Sanitize files for RAG ingest (docs use case)](https://docs.groupdocs.com/metadata/python-net/use-cases/sanitize-files-for-rag-ingest/)
- [Clean documents before they hit your vector store (blog)](https://blog.groupdocs.com/metadata/sanitize-files-for-rag-ingest-python/)
- [Clean metadata with sanitize() - GroupDocs.Metadata for Python](https://docs.groupdocs.com/metadata/python-net/clean-metadata/)
- [Agents and LLM integration - GroupDocs.Metadata for Python](https://docs.groupdocs.com/metadata/python-net/agents-and-llm-integration/)
- [GroupDocs.Metadata for Python via .NET examples](https://github.com/groupdocs-metadata/GroupDocs.Metadata-for-Python-via-.NET)
- [GroupDocs.Metadata forum](https://forum.groupdocs.com/c/metadata/)
