import { useRef } from 'react'
import colors from '../styles/colors'

function FileUpload({ onFilesUploaded, uploadedFiles, onRemoveFile }) {
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files).filter(file => 
      file.name.endsWith('.csv')
    )
    
    if (files.length > 0) {
      onFilesUploaded(files)
    }
    
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.name.endsWith('.csv')
    )
    
    if (files.length > 0) {
      onFilesUploaded(files)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  return (
    <div className="rounded-lg shadow-md p-6" style={{ backgroundColor: colors.background.card }}>
      <h2 className="text-xl font-semibold mb-4" style={{ color: colors.text.primary }}>Upload Pipeline Data</h2>
      
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors"
        style={{ borderColor: colors.border.medium }}
        onMouseEnter={(e) => e.currentTarget.style.borderColor = colors.border.focus}
        onMouseLeave={(e) => e.currentTarget.style.borderColor = colors.border.medium}
        onClick={() => fileInputRef.current?.click()}
      >
        <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48" style={{ color: colors.text.light }}>
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p className="mt-2 text-sm" style={{ color: colors.text.secondary }}>
          <span className="font-semibold" style={{ color: colors.text.link }}>Click to upload</span> or drag and drop
        </p>
        <p className="text-xs mt-1" style={{ color: colors.text.light }}>CSV files only</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold mb-3" style={{ color: colors.text.primary }}>
            Uploaded Files ({uploadedFiles.length})
          </h3>
          <ul className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <li key={index} className="flex items-center justify-between rounded-lg p-3" style={{ backgroundColor: colors.background.hover }}>
                <div className="flex items-center gap-3">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20" style={{ color: colors.status.success }}>
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm" style={{ color: colors.text.primary }}>{file.name}</span>
                  <span className="text-xs" style={{ color: colors.text.light }}>
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
                <button
                  onClick={() => onRemoveFile(index)}
                  className="transition-colors"
                  style={{ color: colors.status.error }}
                  onMouseEnter={(e) => e.target.style.color = colors.button.dangerHover}
                  onMouseLeave={(e) => e.target.style.color = colors.status.error}
                >
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default FileUpload
