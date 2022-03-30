type TValidator = (value: string) => string | void
type TAsyncValidator = (value: string) => Promise<string | void>

export const composeValidators =
  (...validators: (TValidator | TAsyncValidator)[]) =>
  async (value: string): Promise<string | void> => {
    for (const i in validators) {
      const validator = validators[i]
      const error: string | void = await validator(value)
      if (error !== undefined) return error
    }
    return undefined
  }

export default composeValidators
