// InstantSearch can wrap a rejection after unmounting; retain its identity without retaining the error.
const reportedErrors = new WeakSet<object>()

export function markAlgoliaSearchErrorReported(error: unknown): void {
  if (
    (typeof error === 'object' && error !== null) ||
    typeof error === 'function'
  ) {
    reportedErrors.add(error)
  }
}

export function isReportedAlgoliaWrapper(error: unknown): boolean {
  if (
    !(error instanceof Error) ||
    error.message !==
      'Uncaught, unspecified "error" event. ([object Object])' ||
    !('context' in error) ||
    typeof error.context !== 'object' ||
    error.context === null ||
    !('error' in error.context)
  ) {
    return false
  }

  const original = error.context.error
  return (
    ((typeof original === 'object' && original !== null) ||
      typeof original === 'function') &&
    reportedErrors.has(original)
  )
}
