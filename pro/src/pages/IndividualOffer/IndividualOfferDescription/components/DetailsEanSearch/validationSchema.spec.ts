import { generateEanSearchValidationSchema } from './validationSchema'

describe('eanSearchValidationSchema', () => {
  it('should pass with a valid EAN', async () => {
    await expect(
      generateEanSearchValidationSchema(true).validate({
        eanSearch: '1234567890123',
      })
    ).resolves.toBeDefined()

    await expect(
      generateEanSearchValidationSchema(false).validate({
        eanSearch: '1234567890123',
      })
    ).resolves.toBeDefined()
  })

  it('should fail with an invalid EAN', async () => {
    await expect(
      generateEanSearchValidationSchema(true).validate({ eanSearch: 'invalid' })
    ).rejects.toThrow()

    await expect(
      generateEanSearchValidationSchema(false).validate({
        eanSearch: 'invalid',
      })
    ).rejects.toThrow()
  })
})
