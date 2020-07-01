import { checkIfAgeIsEligible } from '../checkIfAgeIsEligible'
import { getOffset } from '../../utils/getOffset'

describe('check if user age is eligible', () => {
  let timezoneOffset

  beforeEach(() => {
    timezoneOffset = getOffset()
  })

  describe('when user is eligible', () => {
    it('should be eligible if user age is 18 years old', () => {
      // Given
      const june_twentyfive_2020 = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
      jest.spyOn(Date, 'now').mockReturnValue(june_twentyfive_2020)
      const birthDate = '01/01/2002'

      // When
      const returnValue = checkIfAgeIsEligible(birthDate)

      // Then
      expect(returnValue).toBe('eligible')
    })

    it('should be eligible the day before his 19th birthday', () => {
      // Given
      const june_twentyfour_2020_23H59M59 = new Date(
        `2020-06-24T23:59:59${timezoneOffset}`
      ).getTime()
      jest.spyOn(Date, 'now').mockReturnValue(june_twentyfour_2020_23H59M59)
      const birthDate = '25/06/2001'

      // When
      const returnValue = checkIfAgeIsEligible(birthDate)

      // Then
      expect(returnValue).toBe('eligible')
    })

    it('should be eligible on his 18th birthday', () => {
      // Given
      const june_twentyFive_2020_00H = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
      jest.spyOn(Date, 'now').mockReturnValue(june_twentyFive_2020_00H)
      const birthDate = '25/06/2002'

      // When
      const returnValue = checkIfAgeIsEligible(birthDate)

      // Then
      expect(returnValue).toBe('eligible')
    })
  })

  describe('when user is not eligible', () => {
    describe('when user is too old', () => {
      it('should not be eligible on his 19th birthday', () => {
        // Given
        const june_twentyFive_2020_00H = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyFive_2020_00H)
        const birthDate = '25/06/2001'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('tooOld')
      })

      it('should not be eligible if user age is 19 years old or older', () => {
        // Given
        const june_twentyFive_2020_00H = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyFive_2020_00H)
        const birthDate = '12/09/1995'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('tooOld')
      })
    })

    describe('when user is almost eligible', () => {
      it('should return bientot if user is 17 years old', () => {
        // Given
        const june_twentyFive_2020_00H = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyFive_2020_00H)
        const birthDate = '01/01/2003'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('soon')
      })

      it('should return bientot the day before his 18th birthday', () => {
        // Given
        const june_twentyfour_2020_23H59M59 = new Date(
          `2020-06-24T23:59:59${timezoneOffset}`
        ).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyfour_2020_23H59M59)
        const birthDate = '25/06/2002'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('soon')
      })

      it('should return bientot on his 17th birthday', () => {
        // Given
        const june_twentyFive_2020_00H = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyFive_2020_00H)
        const birthDate = '25/06/2003'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('soon')
      })
    })

    describe('when user is too young', () => {
      it('should return trop-tot if user age is under 17 years old', () => {
        // Given
        const june_twentyFive_2020_00H = new Date(`2020-06-25T00:00:00${timezoneOffset}`).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyFive_2020_00H)
        const birthDate = '01/01/2009'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('tooYoung')
      })

      it('should return trop-tot the day before his 17th birthday', () => {
        // Given
        const june_twentyfour_2020_23H59M59 = new Date(
          `2020-06-24T23:59:59${timezoneOffset}`
        ).getTime()
        jest.spyOn(Date, 'now').mockReturnValue(june_twentyfour_2020_23H59M59)
        const birthDate = '25/06/2003'

        // When
        const returnValue = checkIfAgeIsEligible(birthDate)

        // Then
        expect(returnValue).toBe('tooYoung')
      })
    })
  })
})
