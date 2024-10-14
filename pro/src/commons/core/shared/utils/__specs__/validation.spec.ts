import { isPasswordValid } from '../validation'

describe('When validating a password', () => {
  it('should be valid if all requirements are met', () => {
    expect(isPasswordValid('User@azerty1')).toEqual(true)
  })

  it('should be invalid if too short', () => {
    expect(isPasswordValid('User@azert1')).toEqual(false)
  })

  it('should be invalid if no number', () => {
    expect(isPasswordValid('User@azertyazer')).toEqual(false)
  })

  it('should be invalid if no special char', () => {
    expect(isPasswordValid('Userazertyazer1')).toEqual(false)
  })

  it('should be invalid if no lower case', () => {
    expect(isPasswordValid('USER@AZERTYAZER1')).toEqual(false)
  })

  it('should be invalid if no upper case', () => {
    expect(isPasswordValid('user@azertyazer1')).toEqual(false)
  })
})
