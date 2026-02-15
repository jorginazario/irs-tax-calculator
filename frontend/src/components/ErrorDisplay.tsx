interface ErrorDisplayProps {
  message: string;
  onDismiss: () => void;
}

export default function ErrorDisplay({ message, onDismiss }: ErrorDisplayProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <svg
            className="mt-0.5 h-5 w-5 shrink-0 text-red-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-red-700">{message}</p>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 text-red-400 hover:text-red-600"
          aria-label="Dismiss error"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
