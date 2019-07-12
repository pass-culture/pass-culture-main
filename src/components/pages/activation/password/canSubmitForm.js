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

  const canSubmit =
    (!pristine && !hasSubmitErrors && !hasValidationErrors) ||
    (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)

  return canSubmit
}

export default canSubmitForm
