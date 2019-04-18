import 'moment-duration-format'

import {
  getDurationFromMinutes,
  getWhatTitleFromLabelAndIsVirtualVenue,
} from '../utils'

describe('src | components | verso | verso-content | verso-content-offer | utils', () => {
  describe('getDurationFromMinutes', () => {
    it('inférieure à une heure', () => {
      // given
      const durationMinutes = 15

      // when
      const duration = getDurationFromMinutes(durationMinutes)

      // then
      expect(duration).toEqual('15m')
    })

    it('égale à une heure ronde', () => {
      // given
      const durationMinutes = 120

      // when
      const duration = getDurationFromMinutes(durationMinutes)

      // then
      expect(duration).toEqual('2h')
    })

    it('superieure à une heure et inférieure à 12h', () => {
      // given
      const durationMinutes = 123

      // when
      const duration = getDurationFromMinutes(durationMinutes)

      // then
      expect(duration).toEqual('2h03')
    })
  })

  describe('getWhatTitleFromLabelAndIsVirtualVenue', () => {
    it('pour une venue physique', () => {
      // given
      const label = 'Musique (sur supports physiques ou en ligne)'
      const isVirtualVenue = false

      // when
      const title = getWhatTitleFromLabelAndIsVirtualVenue(
        label,
        isVirtualVenue
      )

      // then
      expect(title).toEqual('Musique (sur supports physiques)')
    })

    it('pour une venue virtuelle', () => {
      // given
      const label = 'Musique (sur supports physiques ou en ligne)'
      const isVirtualVenue = true

      // when
      const title = getWhatTitleFromLabelAndIsVirtualVenue(
        label,
        isVirtualVenue
      )

      // then
      expect(title).toEqual('Musique (en ligne)')
    })
  })
})
