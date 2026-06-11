import { ValidationError } from 'yup'

import { VenueSettingsNotificationsValidationSchema } from '../schemas'

describe('VenueSettingsNotificationsValidationSchema', () => {
  const validate = async (
    bookingEmail: unknown
  ): Promise<{ value: unknown; errors: string[] }> => {
    try {
      const value = await VenueSettingsNotificationsValidationSchema.validate(
        { bookingEmail },
        { abortEarly: false }
      )
      return { value, errors: [] }
    } catch (error) {
      if (error instanceof ValidationError) {
        return { value: null, errors: error.errors }
      }
      throw error
    }
  }

  it('should accept a valid email', async () => {
    const { value, errors } = await validate('user@example.com')

    expect(errors).toEqual([])
    expect(value).toEqual({ bookingEmail: 'user@example.com' })
  })

  it('should accept null', async () => {
    const { value, errors } = await validate(null)

    expect(errors).toEqual([])
    expect(value).toEqual({ bookingEmail: null })
  })

  it('should transform an empty string to null', async () => {
    const { value, errors } = await validate('')

    expect(errors).toEqual([])
    expect(value).toEqual({ bookingEmail: null })
  })

  it('should transform an undefined value to null', async () => {
    const { value, errors } = await validate(undefined)

    expect(errors).toEqual([])
    expect(value).toEqual({ bookingEmail: null })
  })

  it('should trim the email value', async () => {
    const { value, errors } = await validate('  user@example.com  ')

    expect(errors).toEqual([])
    expect(value).toEqual({ bookingEmail: 'user@example.com' })
  })

  it('should reject an invalid email', async () => {
    const { errors } = await validate('not-an-email')

    expect(errors).toEqual([
      'Veuillez renseigner un email valide, exemple : mail@exemple.com',
    ])
  })

  it('should reject an email missing the domain', async () => {
    const { errors } = await validate('user@')

    expect(errors).toEqual([
      'Veuillez renseigner un email valide, exemple : mail@exemple.com',
    ])
  })
})
