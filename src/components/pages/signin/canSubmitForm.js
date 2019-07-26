const canSubmitForm = formProps => {
  if (!formProps) {
    throw new Error('canSubmitForm: Missing arguments')
  }
  const {
    // https://github.com/final-form/final-form#formstate
    dirtySinceLastSubmit,
    hasSubmitErrors,
    hasValidationErrors,
    pristine,
  } = formProps

  const dirtyWithoutErrors = !pristine && !hasSubmitErrors && !hasValidationErrors
  const dirtySinceLastSubmitWithSubmitErrors =
    !hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit

  return dirtyWithoutErrors || dirtySinceLastSubmitWithSubmitErrors
}

export default canSubmitForm
