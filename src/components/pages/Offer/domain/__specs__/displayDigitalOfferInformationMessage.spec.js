import displayDigitalOfferInformationMessage from '../displayDigitalOfferInformationMessage'

describe('src | components | pages | Offer | domain | getDurationInHours', () => {
  describe('when offer is digital only and has a type that is not refund', () => {
    it('should return true', () => {
      // when
      const type = {
        onlineOnly: true,
      }

      // then
      expect(displayDigitalOfferInformationMessage(type)).toBe(true)
    })
  })

  describe('when offer is not digital only', () => {
    it('should return false', () => {
      // when
      const type = {
        onlineOnly: false,
      }

      // then
      expect(displayDigitalOfferInformationMessage(type)).toBe(false)
    })
  })

  describe('when no type', () => {
    it('should return false by defaut', () => {
      // then
      expect(displayDigitalOfferInformationMessage()).toBe(false)
    })
  })
})
