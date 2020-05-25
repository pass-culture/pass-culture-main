import { getAccountDeletionEmail, getRemainingCreditForGivenCreditLimit } from '../utils'

describe('src | components | pages | profile | utils', () => {
  describe('getRemainingCreditForGivenCreditLimit', () => {
    it('returns wallet balance if lower than max minus actual', () => {
      // given
      const wallet = 100
      const expense = { actual: 0, max: 200 }

      // then
      const result = getRemainingCreditForGivenCreditLimit(wallet)(expense)

      // when
      expect(result).toStrictEqual(100)
    })

    it('returns max minus actual if lower than wallet balance', () => {
      // given
      const wallet = 400
      const expense = { actual: 90, max: 200 }

      // then
      const result = getRemainingCreditForGivenCreditLimit(wallet)(expense)

      // when
      expect(result).toStrictEqual(110)
    })
  })

  describe('getAccountDeletionEmail', () => {
    it('should generate account deletion email from user informations', () => {
      // Given
      const userId = '1234'
      const userEmail = 'user@example.com'

      // When
      const emailBody = getAccountDeletionEmail(userId, userEmail)

      // Then
      expect(emailBody).toBe(
        "mailto:support@passculture.app?subject=Suppression%20de%20mon%20compte%20pass%20Culture&body=Bonjour,%0A%0AJe%20vous%20%C3%A9cris%20afin%20de%20vous%20demander%20la%20suppression%20de%20mon%20compte%20pass%20Culture%20n%C2%B01234,%20associ%C3%A9%20%C3%A0%20l%E2%80%99adresse%20mail%20user@example.com.%0A%0AJ'ai%20conscience%20que%20la%20suppression%20de%20mon%20compte%20entra%C3%AEnera%20l'annulation%20d%C3%A9finitive%20de%20l'ensemble%20de%20mes%20r%C3%A9servations%20en%20cours.%0A%0AJ'ai%2030%20jours%20pour%20me%20r%C3%A9tracter.%20Au-del%C3%A0%20de%20ce%20d%C3%A9lai,%20je%20ne%20pourrai%20plus%20acc%C3%A9der%20%C3%A0%20mon%20compte%20pass%20Culture,%20ni%20au%20cr%C3%A9dit%20%C3%A9ventuellement%20restant.%0A%0ABien%20cordialement,"
      )
    })
  })
})
