type TValidator = (value: string) => string | void
type TAsyncValidator = (value: string) => Promise<string | void>

export const composeValidators =
  (...validators: (TValidator | TAsyncValidator)[]) =>
  async (value: string): Promise<string[] | void> => {
    const mapCallback = async (validator: TValidator | TAsyncValidator) => {
      if (<TValidator>validator) validator(value)
      return await validator(value)
    }
    const validationErrors: string[] = await Promise.all(
      validators.map(mapCallback)
    ).then(errors => errors.filter((err): err is string => err !== undefined))
    return validationErrors.length > 0 ? validationErrors : undefined
  }

export default composeValidators
