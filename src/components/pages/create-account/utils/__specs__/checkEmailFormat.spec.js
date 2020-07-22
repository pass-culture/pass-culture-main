import { handleCheckEmailFormat } from '../checkEmailFormat'

const validEmailList = [
  'validemail@test.com',
  'VALIDEMAIL@test.fr',
  'valid-email@test.com',
  'validemail1234@test.com',
  'valid_email_1234@test1234.com',
]

const invalidEmailList = [
  'invalidemail@@test.com',
  'invalidemail@test..com',
  'invalid@email@test.com',
  '@invalidemail@test.com',
  'invalidemail@test@com',
  'invalidemail.test.com',
  'invalidemail@test.9',
  'invalidemail@test.-',
  'invalidemail@test',
  'invalidemail@.com',
]

describe('check email format', () => {
  it('should return true for a valid email', () => {
    // Given
    const validEmail = 'valid+email@test.com'

    // Then
    expect(handleCheckEmailFormat(validEmail)).toBe(true)
  })

  it('should return false for an invalid email', () => {
    // Given
    const invalidEmail = '.invalid+email@test.com'

    // Then
    expect(handleCheckEmailFormat(invalidEmail)).toBe(false)

  })

  it('should return true foreach email value', () => {
    validEmailList.forEach(email => {
      // Given
      const isEmailValid = handleCheckEmailFormat(email)

      // Then
      expect(isEmailValid).toBe(true)
    })
  })

  it('should return false foreach email value', () => {
    invalidEmailList.forEach(email => {
      // Given
      const isEmailValid = handleCheckEmailFormat(email)

      // Then
      expect(isEmailValid).toBe(false)
    })
  })
})
