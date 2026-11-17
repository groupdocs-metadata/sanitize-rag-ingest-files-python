# Topic: Sanitize Office, PDF and image files before they enter a RAG / LLM ingest pipeline.
# Uses GroupDocs.Metadata for Python via .NET. Inspects inbound metadata, strips it with
# sanitize(), then re-opens the cleaned file to prove identity and EXIF/XMP fields are gone.

from __future__ import annotations

import os
import sys
from pathlib import Path

from groupdocs.metadata import Metadata

DOCS = "documents"
RESULT = "Result"

INCOMING = [
    "incoming.docx",
    "incoming.pdf",
    "incoming.jpg",
]


def apply_license() -> None:
    # Point this at your .lic file to remove evaluation limits.
    # Get a free temporary licence: https://purchase.groupdocs.com/temp-license/100216
    license_path = "REPLACE_WITH_YOUR_LICENSE_PATH"
    if os.path.exists(license_path):
        from groupdocs.metadata import License

        License().set_license(license_path)
        print("[license] applied")
    else:
        print("[license] no licence set - running in evaluation mode")


def inspect_inbound_file_metadata(input_path: str) -> int:
    """
    Inspect metadata on a file before it enters a RAG ingest step.

    Remarks:
        Opens the file with Metadata, prints basic document info, then lists
        every detected property via find_properties. Use this as the pre-clean
        audit so authors, comments, EXIF and XMP are visible before sanitize().
    """
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


def sanitize_file_for_rag_ingest(input_path: str, output_path: str) -> int:
    """
    Strip all detected metadata so a file is safe for RAG / LLM ingest.

    Remarks:
        Calls sanitize() to remove every detected metadata package in one pass
        (authors, comments, revision history, EXIF, XMP and similar), then saves
        a clean copy. Returns the number of properties removed.
    """
    with Metadata(input_path) as metadata:
        removed = metadata.sanitize()
        metadata.save(output_path)
        return int(removed)


def verify_metadata_cleared(cleaned_path: str) -> int:
    """
    Re-open a sanitized file and count remaining metadata properties.

    Remarks:
        Runs find_properties again after sanitize+save. A low remaining count
        is the proof a RAG pipeline can assert before embedding the file.
    """
    with Metadata(cleaned_path) as metadata:
        remaining = 0
        for prop in metadata.find_properties(lambda p: True):
            print(f"{prop.name}={prop.value}")
            remaining += 1
        return remaining


def main() -> int:
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(RESULT, exist_ok=True)
    apply_license()

    processed = 0
    for name in INCOMING:
        source = os.path.join(DOCS, name)
        if not os.path.exists(source):
            print(f"Missing source document: {os.path.abspath(source)}", file=sys.stderr)
            return 1

        stem = Path(name).stem
        suffix = Path(name).suffix
        cleaned = os.path.join(RESULT, f"{stem}-sanitized{suffix}")

        print(f"=== {name}: inspect ===")
        before = inspect_inbound_file_metadata(source)
        print(f"properties_before={before}")

        print(f"=== {name}: sanitize ===")
        removed = sanitize_file_for_rag_ingest(source, cleaned)
        print(f"properties_removed={removed}")
        print(f"cleaned={os.path.abspath(cleaned)}")

        print(f"=== {name}: verify ===")
        after = verify_metadata_cleared(cleaned)
        print(f"properties_after={after}")
        processed += 1

    return 0 if processed == len(INCOMING) else 2


if __name__ == "__main__":
    sys.exit(main())
