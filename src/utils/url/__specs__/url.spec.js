import { versoUrl } from '../url'

describe('src | utils | url | url', () => {
  describe('versoUrl()', () => {
    describe('when offerId and mediationId are given', () => {
      it('should return a URL of offer verso', () => {
        // given
        const offerId = 'ME'
        const mediationId = 'FA'

        // when
        const url = versoUrl(offerId, mediationId)

        // then
        expect(url).toBe('/decouverte/ME/FA/verso')
      })
    })

    describe('when offerId given and without meditationId', () => {
      it('should return a URL of offer verso without mediationId', () => {
        // given
        const offerId = 'ME'
        const mediationId = null

        // when
        const url = versoUrl(offerId, mediationId)

        // then
        expect(url).toBe('/decouverte/ME/verso')
      })
    })
  })
})
