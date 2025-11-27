import { isValidEmail } from '../isValidEmail'

describe('isValidEmail', () => {
  it.each([
    'test',
    'test@',
    'test@test',
    'test.com',
    'test@test.c',
    '@test.com',
  ])('should invalidate the following email address : %s', (email) => {
    expect(isValidEmail(email)).toEqual(false)
  })

  it.each([
    'test@test.co',
    'a.test@test.com',
    'test@test.test.com',
  ])('should validate the following email address : %s', (email) => {
    expect(isValidEmail(email)).toEqual(true)
  })
})
