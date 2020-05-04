import getHumanizeRelativeDate from '../getHumanizeRelativeDate'

describe('src | utils | date | getHumanizeRelativeDate', () => {
  describe('getHumanizeRelativeDate()', () => {
    describe('when there is a null date (e.g.: tuto)', () => {
      it('should return null', () => {
        // given
        const offerDate = null

        // when
        const expected = getHumanizeRelativeDate(offerDate, 'Europe/Paris')

        // then
        expect(expected).toBeNull()
      })
    })

    describe('when there is a bad date format', () => {
      it('should throw "Date invalide"', () => {
        // given
        const offerDate = 'MEFA le bg'

        // when
        const expected = () => getHumanizeRelativeDate(offerDate, 'Europe/Paris')

        // then
        expect(expected).toThrow('Date invalide')
      })
    })

    describe('when the beginning date is not today or tomorrow', () => {
      it('should return null', () => {
        // given
        const offerDate = '2018-07-21T20:00:00Z'

        // when
        const expected = getHumanizeRelativeDate(offerDate, 'Europe/Paris')

        // then
        expect(expected).toBeNull()
      })
    })

    describe('when the beginning date is today', () => {
      it('should return "Aujourd’hui"', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-05-30T20:00:00+02:00')
        const offerDate = '2020-05-30T21:00:00+02:00'

        // when
        const expected = getHumanizeRelativeDate(offerDate, 'Europe/Paris')

        // then
        expect(expected).toBe('Aujourd’hui')
      })
    })

    describe('when the beginning date is tomorrow', () => {
      it('should return "Demain"', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-05-30T20:00:00+02:00')
        const offerDate = '2020-05-31T19:00:00+02:00'

        // when
        const expected = getHumanizeRelativeDate(offerDate, 'Europe/Paris')

        // then
        expect(expected).toBe('Demain')
      })
    })

    describe('when user has a different timezone than the offer (edge cases)', () => {
      const offerDateInLaReunion = '2020-06-01T20:00:00+04:00'
      it('should return nothing when offer date is in more than "Demain"', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-05-30T21:59:59+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBeNull()
      })

      it('should start return "Demain" when offer date start to be tomorrow', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-05-30T22:00:00+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBe('Demain')
      })

      it('should return "Demain" for the last time when offer date is just before today', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-05-31T21:59:59+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBe('Demain')
      })

      it('should start return "Aujourd’hui" when offer date start to be today', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-05-31T22:00:00+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBe('Aujourd’hui')
      })

      it('should return "Aujourd’hui" for the last time when offer is just before to be finished', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-06-01T17:59:59+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBe('Aujourd’hui')
      })

      it('should return nothing when offer date is finished but still today', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-06-01T18:00:01+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBeNull()
      })

      it('should return nothing when offer date is finished since more than today', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => '2020-06-02T18:00:01+02:00')
        const offerDate = new Date(offerDateInLaReunion)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString(), 'Indian/Reunion')

        // then
        expect(expected).toBeNull()
      })
    })
  })
})
