type TValidator = (value: string) => string | void
type TAsyncValidator = (value: string) => Promise<string | void>
type TComposeValidatorsReturn = (string | void) | Promise<string | void>

export const composeValidators =
  (...validators: (TValidator | TAsyncValidator | null | undefined)[]) =>
  (value: string): TComposeValidatorsReturn => {
    for (const i in validators) {
      const validator = validators[i]
      if (!validator) {
        continue
      }

      const error: TComposeValidatorsReturn = validator(value)
      if (error !== undefined) return error
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
    if (type === 'number' && value !== '') return undefined
    if (typeof value === 'string' && value !== '') return undefined
    return error
  }

interface IGetCanSubmitArgs {
  isLoading: boolean
  dirtySinceLastSubmit: boolean
  hasSubmitErrors: boolean
  hasValidationErrors: boolean
  pristine: boolean
}

export const getCanSubmit = (
  config: IGetCanSubmitArgs | undefined
): boolean => {
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

export const parseSubmitErrors = (errors: Record<string, string>) =>
  Object.keys(errors).reduce((acc, key) => {
    // FIXME -> test with a array or errors
    const err = errors[key]
    return { ...acc, [key]: err }
  }, {})
