import { string } from 'yup'

export const nonEmptyStringOrNull = () =>
  string()
    .nullable()
    .default(null) // `undefined` => `null`
    .trim()
    .transform((value) => (value === '' ? null : value))
    .defined() // TS now infers `string | null` instead of `string | null | undefined`
