const hasErrorMessage = meta =>
  meta && meta.submitError && meta.submitError.length ? ' input-error' : ''

export default hasErrorMessage
