"""
Shared Test Fixtures and Environment Initialization.
=====================================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

import sys
import pytest
from pathlib import Path

# Add python package directory to path
repo_root = Path(__file__).resolve().parent.parent
for cand in (repo_root / "python", repo_root):
    if str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from accsify_tesseract import (
    ModelManager,
    ModelType,
    generate_sample_document,
    generate_sample_receipt,
)


@pytest.fixture(scope="session", autouse=True)
def setup_models_and_samples(tmp_path_factory):
    """Ensure required language models and sample images exist for tests."""
    # Ensure eng and ara models are downloaded
    for m in ["eng", "ara"]:
        if not ModelManager.is_installed(m, ModelType.FAST):
            ModelManager.download(m, ModelType.FAST)

    # Pre-generate sample images in shared directory
    samples_dir = repo_root / "tests" / "fixtures"
    samples_dir.mkdir(parents=True, exist_ok=True)

    doc_img = samples_dir / "sample_doc.png"
    if not doc_img.exists():
        generate_sample_document(doc_img)

    receipt_img = samples_dir / "sample_receipt.png"
    if not receipt_img.exists():
        generate_sample_receipt(receipt_img)

    return {
        "doc_image": doc_img,
        "receipt_image": receipt_img,
    }
