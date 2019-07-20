import {
  isFinished,
  mapStateToProps,
  ribbonLabelAndType,
  stringify,
  updatePropsWithDateElements,
} from '../MyBookingContainer'

describe('src | components | pages | my-bookings | MyBookingContainer', () => {
  describe('stringify()', () => {
    it('should stringify and capitalize a date with a time zone', () => {
      // given
      const date = '2019-07-08T20:00:00Z'
      const timeZone = 'Europe/Paris'

      // when
      const stringifyDate = stringify(date)(timeZone)

      // then
      expect(stringifyDate).toBe('Lundi 08/07/2019 à 22:00')
    })
  })

  describe('isFinished()', () => {
    describe('when the reservation is permanent', () => {
      it('should return false', () => {
        // given
        const endDatetime = null

        // when
        const finishedDate = isFinished(endDatetime)

        // then
        expect(finishedDate).toBe(false)
      })
    })

    describe('when the reservation is not finished', () => {
      it('should return false', () => {
        // given
        const endDatetime = '2999-01-01'

        // when
        const finishedDate = isFinished(endDatetime)

        // then
        expect(finishedDate).toBe(false)
      })
    })

    describe('when the reservation is finished', () => {
      it('should return true', () => {
        // given
        const endDatetime = '2010-01-01'

        // when
        const finishedDate = isFinished(endDatetime)

        // then
        expect(finishedDate).toBe(true)
      })
    })
  })

  describe('updatePropsWithDateElements()', () => {
    describe('when there is a beginning date time', () => {
      it('should return a stringify date', () => {
        // given
        const beginningDateTime = '2019-05-15T20:00:00Z'
        const departementCode = '93'

        // when
        const updatedProps = updatePropsWithDateElements(beginningDateTime, departementCode)

        // then
        expect(updatedProps).toBe('Mercredi 15/05/2019 à 22:00')
      })
    })

    describe('when there is not a beginning date time', () => {
      it('should return "Permanent"', () => {
        // given
        const beginningDateTime = null
        const departementCode = '93'

        // when
        const updatedProps = updatePropsWithDateElements(beginningDateTime, departementCode)

        // then
        expect(updatedProps).toBe('Permanent')
      })
    })
  })

  describe('ribbonLabelAndType()', () => {
    describe('when the reservation is today', () => {
      it('should return an object with Aujourd’hui et today', () => {
        // given
        const isCancelled = false
        const isFinished = false
        const humanizeRelativeDate = 'Aujourd’hui'

        // when
        const ribbon = ribbonLabelAndType(isCancelled, isFinished, humanizeRelativeDate)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Aujourd’hui',
          type: 'today',
        })
      })
    })

    describe('when the reservation is tomorrow', () => {
      it('should return an object with Demain and tomorrow', () => {
        // given
        const isCancelled = false
        const isFinished = false
        const humanizeRelativeDate = 'Demain'

        // when
        const ribbon = ribbonLabelAndType(isCancelled, isFinished, humanizeRelativeDate)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Demain',
          type: 'tomorrow',
        })
      })
    })

    describe('when the reservation is finished', () => {
      it('should return an object with Terminé et finished', () => {
        // given
        const isCancelled = false
        const isFinished = true

        // when
        const ribbon = ribbonLabelAndType(isCancelled, isFinished)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Terminé',
          type: 'finished',
        })
      })
    })

    describe('when the reservation is cancelled', () => {
      it('should return an object with Annulé et cancelled', () => {
        // given
        const isCancelled = true
        const isFinished = false

        // when
        const ribbon = ribbonLabelAndType(isCancelled, isFinished)

        // then
        expect(ribbon).toStrictEqual({
          label: 'Annulé',
          type: 'cancelled',
        })
      })
    })

    describe('when the reservation is in progress', () => {
      it('should return null', () => {
        // given
        const isCancelled = false
        const isFinished = false

        // when
        const ribbon = ribbonLabelAndType(isCancelled, isFinished)

        // then
        expect(ribbon).toBeNull()
      })
    })
  })

  describe('mapStateToProps()', () => {
    it('should return props with date elements', () => {
      // given
      const state = {}
      const ownProps = {
        booking: {
          isCancelled: true,
          recommendation: {
            mediationId: 'AAAA',
            thumbUrl: 'https://example.net/mediation/image',
          },
          stock: {
            beginningDatetime: '2019-05-15T20:00:00Z',
            resolvedOffer: {
              id: 'CCCC',
              isEvent: true,
              product: {
                name: 'Fake booking name',
              },
              venue: {
                departementCode: '93',
              },
            },
          },
          token: 'BBBB',
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        name: 'Fake booking name',
        ribbon: {
          label: 'Annulé',
          type: 'cancelled',
        },
        versoUrl: '/decouverte/CCCC/AAAA/verso',
        stringifyDate: 'Mercredi 15/05/2019 à 22:00',
        thumbUrl: 'https://example.net/mediation/image',
        token: 'bbbb',
      })
    })
  })
})
