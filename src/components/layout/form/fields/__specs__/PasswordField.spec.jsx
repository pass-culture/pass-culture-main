import { isNotValid } from '../PasswordField'

describe('component | PasswordField', () => {
  describe('isNotValid', () => {
    it('should return true when has no character', () => {
      const result = isNotValid('')

      expect(result).toStrictEqual(['Ce champ est obligatoire'])
    })

    it('should return false when has at least one character', () => {
      const result = isNotValid('une valeur')

      expect(result).toBeNull()
    })
  })
})
