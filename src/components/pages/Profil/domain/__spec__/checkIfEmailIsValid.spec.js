import { isValidEmail } from '../isValidEmail'

describe('check if email is valid', () => {
  it('should return true for a valid email', () => {
    // Given
    const validEmailList = [
      'valid+email@test.com',
      'validemail@test.com',
      'VALIDEMAIL@test.fr',
      'valid-email@test.com',
      'valid/email@test.com',
      'validemail1234@test.com',
      'valid_email_1234@test1234.com',
    ]
    validEmailList.forEach(email => {
      // When
      const isEmailValid = isValidEmail(email)

      // Then
      expect(isEmailValid).toBe(true)
    })
  })

  it('should return false for an invalid email', () => {
    // Given
    const invalidEmailList = [
      '.invalid+email@test.com',
      'invalidemail@@test.com',
      'invalidemail@test.c',
      'invalidemail@test..com',
      'invalid@email@test.com',
      '@invalidemail@test.com',
      'invalidemail@test@com',
      'invalidemail.test.com',
      'invalidemail@test.9',
      'invalidemail@test.-',
      'email(invalid)@test.com',
      'invalidemail@test',
      'invalidemail@.com',
    ]
    invalidEmailList.forEach(email => {
      // When
      const isEmailValid = isValidEmail(email)

      // Then
      expect(isEmailValid).toBe(false)
    })
  })
})
