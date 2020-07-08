import { handleCheckEmailFormat } from '../checkEmailFormat'

describe('check email format', () => {
  it('should render true for a valid email', () => {
    // Given
    const validEmail = 'valid+email@test.com'

    // Then
    expect(handleCheckEmailFormat(validEmail)).toBe(true)
  })

  it('should render false for an invalid email', () => {
    // Given
    const invalidEmail = '.invalid+email@test.com'

    // Then
    expect(handleCheckEmailFormat(invalidEmail)).toBe(false)

  })
})
