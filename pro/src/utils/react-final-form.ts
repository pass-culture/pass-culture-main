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

export default composeValidators
