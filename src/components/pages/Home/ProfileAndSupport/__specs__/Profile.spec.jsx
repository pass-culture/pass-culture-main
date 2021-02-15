import '@testing-library/jest-dom'

import { formatPhoneNumber } from '../ProfileAndSupport'

describe('profile: formatPhoneNumber', () => {
  it('should format valid phone number', () => {
    const phoneNumber = '0123456789'
    expect(formatPhoneNumber(phoneNumber)).toBe('01 23 45 67 89')
  })

  it('should format phone number with extra whitespaces', () => {
    const phoneNumber = '01   23  4  56 7 8 9'
    expect(formatPhoneNumber(phoneNumber)).toBe('01 23 45 67 89')
  })

  it('should format valid international phone number', () => {
    const phoneNumber = '+33123456789'
    expect(formatPhoneNumber(phoneNumber)).toBe('+33 1 23 45 67 89')
  })

  it('should format international phone number with extra whitespaces', () => {
    const phoneNumber = '+ 3 31   23  4  56 7 8 9'
    expect(formatPhoneNumber(phoneNumber)).toBe('+33 1 23 45 67 89')
  })

  it('should not format empty phoneNumber', () => {
    const phoneNumber = ''
    expect(formatPhoneNumber(phoneNumber)).toBe(phoneNumber)
  })

  it('should not format null phoneNumber', () => {
    const phoneNumber = null
    expect(formatPhoneNumber(phoneNumber)).toBe(phoneNumber)
  })

  it("should not format phone number with more than 10 digits if it's not a valid international phone number", () => {
    const phoneNumber = '333123456789'
    expect(formatPhoneNumber(phoneNumber)).toBe(phoneNumber)
  })

  it('should not format phone number with less than 10 digits', () => {
    const phoneNumber = '012345678'
    expect(formatPhoneNumber(phoneNumber)).toBe(phoneNumber)
  })

  it('should not format phone number that container a letter', () => {
    const phoneNumber = '0123BC6789'
    expect(formatPhoneNumber(phoneNumber)).toBe(phoneNumber)
  })

  it('should not format phoneNumber that container a "+" letter', () => {
    const phoneNumber = '01234+6789'
    expect(formatPhoneNumber(phoneNumber)).toBe(phoneNumber)
  })
})
