import type * as yup from 'yup'

import { validationSchema } from './validationSchema'

describe('validationSchema', () => {
  it('validates a correct email', async () => {
    await expect(
      validationSchema.isValid({ email: 'test@example.com' })
    ).resolves.toBe(true)
  })

  it('rejects an empty email', async () => {
    await expect(validationSchema.isValid({ email: '' })).resolves.toBe(false)
  })

  it('rejects an invalid email format', async () => {
    await expect(
      validationSchema.isValid({ email: 'not-an-email' })
    ).resolves.toBe(false)
  })

  it('rejects an email longer than 120 characters', async () => {
    const longEmail = `${'a'.repeat(116)}@a.co`
    expect(longEmail.length).toBeGreaterThan(120)

    await expect(validationSchema.isValid({ email: longEmail })).resolves.toBe(
      false
    )
  })

  it('returns the expected message when the email is missing', async () => {
    await expect(
      validationSchema.validate({ email: '' })
    ).rejects.toMatchObject({
      message: 'Veuillez renseigner une adresse email',
    } satisfies Partial<yup.ValidationError>)
  })
})
