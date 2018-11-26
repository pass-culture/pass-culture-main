// jest --env=jsdom ./src/components/forms/validators/tests/strings --watch
import { strings } from '../strings'

describe('src | components | forms | validators | tests | strings', () => {
  it('test DEFAULT_REQUIRED_ERROR error string', () => {
    const expected = 'Ce champs est requis.'
    expect(strings.DEFAULT_REQUIRED_ERROR).toEqual(expected)
  })
  it('test PASSORD_ERROR_IS_EQUAL_ORIGINAL error string', () => {
    const expected =
      'Votre nouveau mot de passe doit être différent de votre ancien mot de passe.'
    expect(strings.PASSORD_ERROR_IS_EQUAL_ORIGINAL).toEqual(expected)
  })
  it('test PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM error string', () => {
    const expected = 'Les deux mots de passe ne sont pas identiques.'
    expect(strings.PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM).toEqual(expected)
  })
  it('test PASSWORD_ERROR_MESSAGE error string', () => {
    const expected =
      'Le mot de passe doit contenir au minimum 12 caractères, un chiffre, une majuscule, une minuscule et un caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
    expect(strings.PASSWORD_ERROR_MESSAGE).toEqual(expected)
  })
})
