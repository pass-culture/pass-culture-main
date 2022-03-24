type TValidator = (value: string) => string | void
type TAsyncValidator = (value: string) => Promise<string | void>

export const composeValidators =
  (...validators: (TValidator | TAsyncValidator)[]) =>
  async (value: string) => {
    const mapCallback = async (validator: TValidator | TAsyncValidator) => {
      if (<TValidator>validator) validator(value)
      return await validator(value)
    }
    const validationErrors: (string | void)[] = await Promise.all(
      validators.map(mapCallback)
    ).then(errors => errors.filter(err => err !== undefined))
    return validationErrors.length > 0 ? validationErrors : undefined
  }

export default composeValidators
