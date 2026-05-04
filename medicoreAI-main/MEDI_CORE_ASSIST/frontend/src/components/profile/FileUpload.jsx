import { useMemo, useState } from 'react';
import { FileText, Loader2, Trash2, Upload } from 'lucide-react';
import { getApiBase } from '../../api/client';

const ACCEPTED_TYPES = '.pdf,.jpg,.jpeg,.png';

export default function FileUpload({
  files,
  onUpload,
  onRemove,
  isUploading = false,
}) {
  const [selectedFiles, setSelectedFiles] = useState([]);

  const filePreviews = useMemo(() => {
    return files.map((file) => {
      const absoluteUrl = file.file_url.startsWith('http')
        ? file.file_url
        : `${getApiBase()}${file.file_url}`;
      return { ...file, absoluteUrl };
    });
  }, [files]);

  async function handleUploadClick() {
    if (!selectedFiles.length) {
      return;
    }
    await onUpload(selectedFiles);
    setSelectedFiles([]);
  }

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-slate-700">Prescription Files</label>
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <label className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-white px-4 py-6 text-sm text-slate-600 transition hover:border-emerald-300 hover:bg-emerald-50/30">
          <Upload className="h-4 w-4" />
          Select PDF/JPG/PNG files
          <input
            type="file"
            accept={ACCEPTED_TYPES}
            multiple
            className="hidden"
            onChange={(event) => setSelectedFiles(Array.from(event.target.files || []))}
          />
        </label>

        {selectedFiles.length > 0 && (
          <div className="mt-3 rounded-xl bg-white p-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Selected ({selectedFiles.length})
            </p>
            <ul className="mt-2 space-y-1 text-sm text-slate-600">
              {selectedFiles.map((file) => (
                <li key={`${file.name}-${file.size}`}>{file.name}</li>
              ))}
            </ul>
            <button
              type="button"
              onClick={handleUploadClick}
              disabled={isUploading}
              className="btn-primary mt-3 w-full"
            >
              {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              {isUploading ? 'Uploading...' : 'Upload Prescriptions'}
            </button>
          </div>
        )}
      </div>

      {filePreviews.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Uploaded Files
          </p>
          <ul className="space-y-2">
            {filePreviews.map((file, index) => (
              <li
                key={file.id}
                className="flex items-center gap-3 rounded-lg bg-slate-50 px-3 py-2"
              >
                <FileText className="h-4 w-4 text-slate-500" />
                <a
                  href={file.absoluteUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 truncate text-sm text-emerald-700 hover:text-emerald-600"
                >
                  {file.file_name}
                </a>
                <button
                  type="button"
                  onClick={() => onRemove(index)}
                  className="rounded-md p-1.5 text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
