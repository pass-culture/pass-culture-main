import * as yup from 'yup'

import { readonly } from '../readonly'

describe('readonly', () => {
  it('should preserve original string after a preceding trimming transform logic', async () => {
    const schema = yup
      .string()
      .transform((v) => (typeof v === 'string' ? v.trim() : v))
      .transform(readonly)
    const input = '  abc  '

    const result = await schema.validate(input)

    expect(result).toBe(input)
  })

  it('should keep null and undefined unchanged', async () => {
    const schema = yup
      .string()
      .nullable()
      .transform((s) => s?.trim())
      .transform(readonly)

    await expect(schema.validate(null)).resolves.toBeNull()
    // For undefined, yup will typically treat it as undefined unless required()
    const optionalSchema = yup.string().transform(readonly)

    const result = await optionalSchema.validate(undefined)

    expect(result).toBeUndefined()
  })
})
