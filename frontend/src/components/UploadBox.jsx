import React, { useRef, useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, X, RefreshCw } from 'lucide-react';
import Button from './Button';

export default function UploadBox({
  file,
  onFileSelect,
  onFileRemove,
  error,
  disabled = false,
}) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    const droppedFiles = e.dataTransfer?.files;
    if (droppedFiles && droppedFiles.length > 0) {
      validateAndProcess(droppedFiles[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      validateAndProcess(selectedFiles[0]);
    }
  };

  const validateAndProcess = (selectedFile) => {
    if (!selectedFile) return;

    // Check extension and MIME type for PDF
    const isPdf =
      selectedFile.type === 'application/pdf' ||
      selectedFile.name.toLowerCase().endsWith('.pdf');

    if (!isPdf) {
      onFileSelect(null, 'Only PDF files are supported. Please upload a .pdf document.');
      return;
    }

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      onFileSelect(null, 'File size exceeds 10MB limit. Please upload a smaller PDF.');
      return;
    }

    if (selectedFile.size === 0) {
      onFileSelect(null, 'The selected file is empty. Please upload a valid resume PDF.');
      return;
    }

    onFileSelect(selectedFile, null);
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 KB';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        accept=".pdf,application/pdf"
        className="hidden"
        disabled={disabled}
      />

      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
          className={`group relative flex flex-col items-center justify-center p-8 sm:p-10 border-2 border-dashed rounded-3xl transition-all cursor-pointer ${
            isDragging
              ? 'border-[#0a152d] bg-gray-50/80 scale-[0.99]'
              : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50/40'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="w-14 h-14 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#0a1b33] mb-4 group-hover:scale-105 transition-transform shadow-xs">
            <Upload className="w-6 h-6 text-[#0a1b33]" />
          </div>

          <p className="font-display font-semibold text-base sm:text-lg text-[#0a1b33] mb-1 text-center">
            Upload your resume PDF
          </p>
          <p className="text-xs sm:text-sm text-gray-500 mb-4 text-center max-w-sm">
            Drag and drop your file here, or click to browse from your device
          </p>

          <Button
            variant="secondary"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={disabled}
          >
            Select PDF File
          </Button>

          <span className="mt-3 text-[11px] text-gray-400 font-medium">
            Strictly PDF only • Up to 10 MB
          </span>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-3xl p-5 sm:p-6 shadow-xs">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3.5 min-w-0">
              <div className="w-12 h-12 rounded-2xl bg-gray-100 border border-gray-200/80 flex items-center justify-center text-[#0a152d] shrink-0">
                <FileText className="w-6 h-6" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-sm sm:text-base text-[#0a1b33] truncate max-w-[220px] sm:max-w-xs md:max-w-md">
                    {file.name}
                  </p>
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full shrink-0">
                    <CheckCircle2 className="w-3 h-3" /> Ready
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">
                  {formatFileSize(file.size)} • PDF Document
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto justify-end pt-2 sm:pt-0 border-t sm:border-t-0 border-gray-100">
              <Button
                variant="secondary"
                size="sm"
                icon={RefreshCw}
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
              >
                Replace
              </Button>
              <Button
                variant="outline"
                size="sm"
                icon={X}
                onClick={onFileRemove}
                disabled={disabled}
              >
                Remove
              </Button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-start gap-2 p-3 bg-red-50 border border-red-100 rounded-2xl text-xs sm:text-sm text-red-700">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
