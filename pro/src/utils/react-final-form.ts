type Validator = (value: string) => string | void
type AsyncValidator = (value: string) => Promise<string | void>
type ComposeValidatorsReturn = (string | void) | Promise<string | void>

export const composeValidators =
  (...validators: (Validator | AsyncValidator | null | undefined)[]) =>
  (value: string): ComposeValidatorsReturn => {
    for (const i in validators) {
      const validator = validators[i]
      if (!validator) {
        continue
      }

      const error: ComposeValidatorsReturn = validator(value)
      if (error !== undefined) {
        return error
      }
    }
    return undefined
  }

export const createParseNumberValue =
  (type: 'number' | 'text') =>
  (value: number | string): string | number | null => {
    if (typeof value === undefined) {
      return null
    }

    let stringValue: string | number = String(value)
    if (stringValue === '') {
      return ''
    }

    if (type === 'number') {
      if (stringValue.includes(',')) {
        stringValue = stringValue.replace(/,/g, '.')
      }

      stringValue = stringValue.includes('.')
        ? parseFloat(stringValue)
        : parseInt(stringValue, 10)
    }

    return stringValue
  }

export const createValidateRequiredField =
  (error: string, type?: 'text' | 'number') => (value: string) => {
    if (type === 'number' && value !== '') {
      return undefined
    }
    if (typeof value === 'string' && value !== '') {
      return undefined
    }
    return error
  }

interface GetCanSubmitArgs {
  isLoading: boolean
  dirtySinceLastSubmit: boolean
  hasSubmitErrors: boolean
  hasValidationErrors: boolean
  pristine: boolean
}

export const getCanSubmit = (config: GetCanSubmitArgs | undefined): boolean => {
  if (config === undefined) {
    throw new Error('getCanSubmit: Missing arguments')
  }

  const {
    isLoading,
    dirtySinceLastSubmit,
    hasSubmitErrors,
    hasValidationErrors,
    pristine,
  } = config

  const canSubmit =
    !isLoading &&
    ((!pristine && !hasSubmitErrors && !hasValidationErrors) ||
      (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit))

  return canSubmit
}
