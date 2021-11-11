import 'moment-duration-format'

import getDurationFromMinutes from '../getDurationFromMinutes'

describe('src | components | verso | verso-content | verso-content-offer | utils', () => {
  describe('getDurationFromMinutes', () => {
    it('inférieure à une heure', () => {
      // given
      const durationMinutes = 15

      // when
      const duration = getDurationFromMinutes(durationMinutes)

      // then
      expect(duration).toStrictEqual('15m')
    })

    it('égale à une heure ronde', () => {
      // given
      const durationMinutes = 120

      // when
      const duration = getDurationFromMinutes(durationMinutes)

      // then
      expect(duration).toStrictEqual('2h')
    })

    it('superieure à une heure et inférieure à 12h', () => {
      // given
      const durationMinutes = 123

      // when
      const duration = getDurationFromMinutes(durationMinutes)

      // then
      expect(duration).toStrictEqual('2h03')
    })
  })
})
