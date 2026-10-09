import { useRef, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi } from '../../services/api'
import { Document as Doc, ProcessingStatus } from '../../types'
import {
  Upload, Loader2, FileText, AlertCircle, CheckCircle,
  Clock, RefreshCw, FolderOpen,
} from 'lucide-react'
import { format } from 'date-fns'

const STATUS_META: Record<ProcessingStatus, {
  icon: React.ReactNode; label: string; color: string
}> = {
  UPLOADED:   { icon: <Clock       className="w-3.5 h-3.5" />, label: 'Queued',     color: '#8B7550' },
  PROCESSING: { icon: <Loader2     className="w-3.5 h-3.5 animate-spin" />, label: 'Processing', color: '#AA9164' },
  PROCESSED:  { icon: <CheckCircle className="w-3.5 h-3.5" />, label: 'Processed',  color: '#4A6B4A' },
  FAILED:     { icon: <AlertCircle className="w-3.5 h-3.5" />, label: 'Failed',     color: '#8B3535' },
}

function DocRow({ doc, caseId }: { doc: Doc; caseId: string }) {
  const qc = useQueryClient()
  const meta = STATUS_META[doc.processing_status]
  const sizeKb = doc.file_size_bytes ? (doc.file_size_bytes / 1024).toFixed(1) : '?'

  const { mutate: reprocess, isPending } = useMutation({
    mutationFn: () => documentsApi.reprocess(caseId, doc.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', caseId] }),
  })

  return (
    <div
      className="flex items-center gap-4 px-4 py-3 border-b border-wire/60 last:border-0
                 hover:bg-walnut/30 transition-colors"
    >
      <FileText className="w-4 h-4 text-sepia/50 flex-shrink-0" />

      <div className="flex-1 min-w-0">
        <p className="text-sm text-parchment font-sans truncate">{doc.original_filename}</p>
        <p className="text-[10px] font-mono text-sepia/60 mt-0.5">
          {doc.document_type} · {sizeKb} KB ·{' '}
          {format(new Date(doc.uploaded_at), 'dd MMM yyyy, HH:mm')}
        </p>
        {doc.processing_error && (
          <p className="text-[10px] text-burgundy-light mt-0.5 truncate font-mono">
            {doc.processing_error.slice(0, 80)}
          </p>
        )}
      </div>

      {/* Status */}
      <div
        className="flex items-center gap-1.5 text-xs font-mono flex-shrink-0"
        style={{ color: meta.color }}
      >
        {meta.icon}
        {meta.label}
      </div>

      {/* Reprocess */}
      {doc.processing_status === 'FAILED' && (
        <button
          onClick={() => reprocess()}
          disabled={isPending}
          className="text-sepia hover:text-parchment transition-colors flex-shrink-0"
          title="Reprocess"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isPending ? 'animate-spin' : ''}`} />
        </button>
      )}
    </div>
  )
}

export default function CaseDocumentsTab({ caseId }: { caseId: string }) {
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['documents', caseId],
    queryFn:  () => documentsApi.list(caseId),
    refetchInterval: (query) => {
      const docs: Doc[] = query.state.data?.data ?? []
      return docs.some(
        (d) => d.processing_status === 'UPLOADED' || d.processing_status === 'PROCESSING'
      ) ? 3000 : false
    },
  })
  const docs: Doc[] = data?.data ?? []

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadError('')
    try {
      await documentsApi.upload(caseId, file)
      qc.invalidateQueries({ queryKey: ['documents', caseId] })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail
      setUploadError(msg || 'Upload failed. Check file type and size.')
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div className="p-6">

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="font-serif text-base font-semibold text-cream">Evidence Files</h2>
          <p className="text-xs text-sepia font-sans mt-0.5">
            Supported: PDF, TXT, DOCX, CSV, JSON · Max 50 MB
          </p>
        </div>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.docx,.csv,.json"
            onChange={handleFile}
            className="hidden"
            id="doc-upload"
          />
          <label
            htmlFor="doc-upload"
            className={`btn-primary flex items-center gap-2 cursor-pointer
                        ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
          >
            {uploading
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Uploading…</>
              : <><Upload className="w-4 h-4" /> Upload Evidence</>
            }
          </label>
        </div>
      </div>

      {/* Error */}
      {uploadError && (
        <div className="flex items-center gap-2 text-sm bg-burgundy/10
                        border border-burgundy/30 rounded-file px-3 py-2 mb-4">
          <AlertCircle className="w-4 h-4 text-burgundy-light flex-shrink-0" />
          <span className="text-burgundy-light text-xs">{uploadError}</span>
        </div>
      )}

      {/* File list */}
      <div className="card p-0 overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-10">
            <Loader2 className="w-5 h-5 animate-spin text-brass" />
          </div>
        ) : docs.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen className="w-8 h-8 text-sepia/20 mx-auto mb-3" />
            <p className="font-serif text-sm text-parchment mb-1">No files on file</p>
            <p className="text-xs text-sepia font-sans">
              Upload investigation documents to begin extraction.
            </p>
          </div>
        ) : (
          docs.map((d) => <DocRow key={d.id} doc={d} caseId={caseId} />)
        )}
      </div>
    </div>
  )
}
