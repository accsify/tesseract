/**
 * @file accsify_tesseract.h
 * @brief Master C/C++ Header for Accsify Tesseract OCR Engine.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
 */

#ifndef ACCSIFY_TESSERACT_H
#define ACCSIFY_TESSERACT_H

#include "tesseract_engine.h"

#ifdef __cplusplus
#include "tesseract_engine_cpp.hpp"

namespace accsify {
    using TesseractEngine = accsi::TesseractEngine;
    using TesseractIterator = accsi::TesseractIterator;
    using ModelManager = accsi::ModelManager;
}
#endif

#endif /* ACCSIFY_TESSERACT_H */
