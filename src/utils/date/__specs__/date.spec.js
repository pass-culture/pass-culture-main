import { humanizeRelativeDate } from '../date'

describe('src | utils | date | date', () => {
  describe('humanizeRelativeDate()', () => {
    describe('when there is a null date (e.g.: tuto)', () => {
      it('should return null', () => {
        // given
        const offerDate = null

        // when
        const expected = humanizeRelativeDate(offerDate)

        // then
        expect(expected).toBeNull()
      })
    })

    describe('when there is a bad date format', () => {
      it('should throw "Date invalide"', () => {
        // given
        const offerDate = 'MEFA'

        // when
        const expected = () => humanizeRelativeDate(offerDate)

        // then
        expect(expected).toThrow('Date invalide')
      })
    })

    describe('when the beginning date is not today or tomorrow', () => {
      it('should return null', () => {
        // given
        const offerDate = '2018-07-21T20:00:00Z'

        // when
        const expected = humanizeRelativeDate(offerDate)

        // then
        expect(expected).toBeNull()
      })
    })

    describe('when the beginning date is today', () => {
      it('should return "Aujourd’hui"', () => {
        // given
        const offerDate = new Date().toISOString()

        // when
        const expected = humanizeRelativeDate(offerDate)

        // then
        expect(expected).toBe('Aujourd’hui')
      })
    })

    describe('when the beginning date is tomorrow', () => {
      it('should return "Demain"', () => {
        // given
        const today = new Date()
        const offerDate = new Date(today)
        const currentDate = today.getDate()
        offerDate.setDate(currentDate + 1)

        // when
        const expected = humanizeRelativeDate(offerDate)

        // then
        expect(expected).toBe('Demain')
      })
    })
  })
})
