import React from 'react';
import { FileText, Calendar, HardDrive, CheckCircle } from 'lucide-react';
import Button from './Button';

export default function ResumeCard({
  resume,
  onSelect,
  isSelected = false,
  className = '',
}) {
  return (
    <div
      onClick={onSelect}
      className={`p-5 rounded-3xl border transition-all cursor-pointer ${
        isSelected
          ? 'bg-white border-[#0a152d] shadow-sm ring-1 ring-[#0a152d]'
          : 'bg-white border-gray-200 hover:border-gray-300 shadow-xs'
      } ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#0a1b33] shrink-0 mt-0.5">
            <FileText className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h4 className="font-semibold text-sm text-[#0a1b33] truncate">
              {resume.filename || 'Resume.pdf'}
            </h4>
            <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {resume.uploaded_at || 'Just now'}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <HardDrive className="w-3 h-3" />
                {resume.file_size || '340 KB'}
              </span>
            </div>
          </div>
        </div>

        {isSelected ? (
          <span className="flex items-center gap-1 text-xs font-semibold text-[#0a152d] bg-gray-100 px-2.5 py-1 rounded-full">
            <CheckCircle className="w-3.5 h-3.5 text-[#0a152d]" /> Selected
          </span>
        ) : (
          <Button variant="ghost" size="sm">
            Select
          </Button>
        )}
      </div>
    </div>
  );
}
