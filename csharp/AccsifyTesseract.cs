/**
 * @file AccsifyTesseract.cs
 * @brief High-Performance C# P/Invoke wrapper for Accsify Tesseract OCR Engine.
 * @company accsify
 * @copyright Copyright (C) 2026 accsify. All rights reserved.
 */

using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace Accsify.Tesseract
{
    public enum PageSegMode
    {
        OsdOnly = 0,
        AutoOsd = 1,
        AutoOnly = 2,
        Auto = 3,
        SingleColumn = 4,
        SingleBlockVertText = 5,
        SingleBlock = 6,
        SingleLine = 7,
        SingleWord = 8,
        CircleWord = 9,
        SingleChar = 10,
        SparseText = 11,
        SparseTextOsd = 12,
        RawLine = 13
    }

    public enum OcrEngineMode
    {
        TesseractOnly = 0,
        LstmOnly = 1,
        TesseractLstmCombined = 2,
        Default = 3
    }

    public enum PageIteratorLevel
    {
        Block = 0,
        Para = 1,
        TextLine = 2,
        Word = 3,
        Symbol = 4
    }

    public enum WritingDirection
    {
        LeftToRight = 0,
        RightToLeft = 1,
        TopToBottom = 2
    }

    public enum TextlineOrder
    {
        LeftToRight = 0,
        RightToLeft = 1,
        TopToBottom = 2
    }

    public enum ModelType
    {
        Fast = 0,
        Best = 1,
        Standard = 2,
        Script = 3
    }

    [StructLayout(LayoutKind.Sequential, Pack = 8)]
    public struct BoundingBox
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;

        public int Width => Math.Max(0, Right - Left);
        public int Height => Math.Max(0, Bottom - Top);

        public override string ToString() => $"[{Left},{Top},{Right},{Bottom}]";
    }

    [StructLayout(LayoutKind.Sequential, Pack = 8, CharSet = CharSet.Ansi)]
    public struct ModelInfo
    {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
        public string Name;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
        public string DisplayName;

        public int Type;
        public long FileSize;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)]
        public string DownloadUrl;

        public int IsInstalled;
    }

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    public delegate int DownloadProgressCallback(
        string modelName,
        int modelType,
        long bytesDownloaded,
        long totalBytes,
        double percentage,
        string statusMessage,
        IntPtr userData
    );

    internal static class NativeMethods
    {
        private const string DllName = "tesseract_engine.dll";

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_version();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_create();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void tess_destroy(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_init(IntPtr handle, string datapath, string language, int oem);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_is_initialized(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_set_variable(IntPtr handle, string name, string value);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_get_variable(IntPtr handle, string name, StringBuilder buffer, int maxLen);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void tess_set_page_seg_mode(IntPtr handle, int psm);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_get_page_seg_mode(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void tess_set_source_resolution(IntPtr handle, int ppi);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_set_image_file(IntPtr handle, string filepath);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_set_image_bytes(IntPtr handle, byte[] data, UIntPtr length);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_set_image_raw(IntPtr handle, byte[] data, int width, int height, int bpp, int bpl);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_recognize(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_get_utf8_text(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_get_hocr_text(IntPtr handle, int pageNum);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_get_tsv_text(IntPtr handle, int pageNum);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_get_box_text(IntPtr handle, int pageNum);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_get_unlv_text(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_get_mean_confidence(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void tess_free_text(IntPtr text);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_detect_orientation_script(
            IntPtr handle, out int orientDeg, out float orientConf,
            StringBuilder scriptName, int maxLen, out float scriptConf);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_get_iterator(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_iterator_next(IntPtr iter, int level);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_iterator_get_bounding_box(
            IntPtr iter, int level, out int left, out int top, out int right, out int bottom);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr tess_iterator_get_text(IntPtr iter, int level);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern float tess_iterator_get_confidence(IntPtr iter, int level);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_iterator_get_writing_direction(IntPtr iter, out int direction);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_iterator_get_textline_order(IntPtr iter, out int order);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_iterator_get_deskew_angle(IntPtr iter, out float angle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void tess_iterator_destroy(IntPtr iter);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_set_path(string path);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_get_path(StringBuilder buffer, int maxLen);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_get_default_path(StringBuilder buffer, int maxLen);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_is_installed(string modelName, int modelType);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_get_catalog_count(int modelType);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_get_catalog_item(int modelType, int index, out ModelInfo outInfo);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_download(
            string modelName, int modelType, DownloadProgressCallback callback, IntPtr userData);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_get_installed_count();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int tess_model_get_installed_item(int index, StringBuilder outName, int maxLen);
    }

    public class TesseractEngine : IDisposable
    {
        private IntPtr _handle;

        public TesseractEngine(string datapath = null, string language = "eng", OcrEngineMode oem = OcrEngineMode.Default)
        {
            _handle = NativeMethods.tess_create();
            if (_handle == IntPtr.Zero)
                throw new OutOfMemoryException("Failed to allocate Tesseract engine handle.");

            int res = NativeMethods.tess_init(_handle, datapath, language, (int)oem);
            if (res != 0)
            {
                Dispose();
                throw new InvalidOperationException($"Failed to initialize engine with language '{language}'. Error code: {res}");
            }
        }

        public static string Version
        {
            get
            {
                IntPtr ptr = NativeMethods.tess_version();
                return Marshal.PtrToStringAnsi(ptr);
            }
        }

        public void SetPageSegMode(PageSegMode psm) => NativeMethods.tess_set_page_seg_mode(_handle, (int)psm);
        public PageSegMode GetPageSegMode() => (PageSegMode)NativeMethods.tess_get_page_seg_mode(_handle);
        public void SetResolution(int ppi) => NativeMethods.tess_set_source_resolution(_handle, ppi);

        public bool SetVariable(string name, string value) => NativeMethods.tess_set_variable(_handle, name, value) != 0;

        public string GetVariable(string name)
        {
            var sb = new StringBuilder(256);
            if (NativeMethods.tess_get_variable(_handle, name, sb, sb.Capacity) != 0)
                return sb.ToString();
            return null;
        }

        public void SetImage(string filepath)
        {
            if (!File.Exists(filepath))
                throw new FileNotFoundException("Image file not found", filepath);
            int res = NativeMethods.tess_set_image_file(_handle, filepath);
            if (res != 0)
                throw new InvalidOperationException($"Failed to load image file: {filepath}");
        }

        public void SetImage(byte[] imageBytes)
        {
            int res = NativeMethods.tess_set_image_bytes(_handle, imageBytes, (UIntPtr)imageBytes.Length);
            if (res != 0)
                throw new InvalidOperationException("Failed to decode image from memory buffer.");
        }

        public void Recognize()
        {
            int res = NativeMethods.tess_recognize(_handle);
            if (res != 0)
                throw new InvalidOperationException("Recognition failed.");
        }

        public string GetText() => ExtractAndFreeText(NativeMethods.tess_get_utf8_text(_handle));
        public string GetHocr(int pageNum = 0) => ExtractAndFreeText(NativeMethods.tess_get_hocr_text(_handle, pageNum));
        public string GetTsv(int pageNum = 0) => ExtractAndFreeText(NativeMethods.tess_get_tsv_text(_handle, pageNum));
        public string GetBox(int pageNum = 0) => ExtractAndFreeText(NativeMethods.tess_get_box_text(_handle, pageNum));
        public string GetUnlv() => ExtractAndFreeText(NativeMethods.tess_get_unlv_text(_handle));

        public int MeanConfidence => NativeMethods.tess_get_mean_confidence(_handle);

        public void DetectOrientationAndScript(out int orientDeg, out float orientConf, out string scriptName, out float scriptConf)
        {
            var sb = new StringBuilder(64);
            int res = NativeMethods.tess_detect_orientation_script(_handle, out orientDeg, out orientConf, sb, 64, out scriptConf);
            if (res != 0)
                throw new InvalidOperationException("Orientation and Script detection failed. Ensure 'osd.traineddata' is present.");
            scriptName = sb.ToString();
        }

        private static string ExtractAndFreeText(IntPtr ptr)
        {
            if (ptr == IntPtr.Zero) return string.Empty;
            try
            {
                int len = 0;
                while (Marshal.ReadByte(ptr, len) != 0) ++len;
                byte[] buffer = new byte[len];
                Marshal.Copy(ptr, buffer, 0, len);
                return Encoding.UTF8.GetString(buffer);
            }
            finally
            {
                NativeMethods.tess_free_text(ptr);
            }
        }

        public void Dispose()
        {
            if (_handle != IntPtr.Zero)
            {
                NativeMethods.tess_destroy(_handle);
                _handle = IntPtr.Zero;
            }
            GC.SuppressFinalize(this);
        }

        ~TesseractEngine() => Dispose();
    }

    public static class ModelManager
    {
        public static void SetPath(string path) => NativeMethods.tess_model_set_path(path);

        public static string GetPath()
        {
            var sb = new StringBuilder(512);
            NativeMethods.tess_model_get_path(sb, sb.Capacity);
            return sb.ToString();
        }

        public static string GetDefaultPath()
        {
            var sb = new StringBuilder(512);
            NativeMethods.tess_model_get_default_path(sb, sb.Capacity);
            return sb.ToString();
        }

        public static bool IsInstalled(string modelName, ModelType type = ModelType.Fast) =>
            NativeMethods.tess_model_is_installed(modelName, (int)type) != 0;

        public static List<ModelInfo> ListCatalog(ModelType? filter = null)
        {
            int t = filter.HasValue ? (int)filter.Value : -1;
            int count = NativeMethods.tess_model_get_catalog_count(t);
            var list = new List<ModelInfo>(count);
            for (int i = 0; i < count; ++i)
            {
                if (NativeMethods.tess_model_get_catalog_item(t, i, out ModelInfo info) == 0)
                    list.Add(info);
            }
            return list;
        }

        public static List<string> ListInstalled()
        {
            int count = NativeMethods.tess_model_get_installed_count();
            var list = new List<string>(count);
            var sb = new StringBuilder(128);
            for (int i = 0; i < count; ++i)
            {
                if (NativeMethods.tess_model_get_installed_item(i, sb, sb.Capacity) == 0)
                    list.Add(sb.ToString());
            }
            return list;
        }

        public static bool Download(string modelName, ModelType type = ModelType.Fast, DownloadProgressCallback callback = null)
        {
            return NativeMethods.tess_model_download(modelName, (int)type, callback, IntPtr.Zero) == 0;
        }
    }
}
