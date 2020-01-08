import displayDigitalOfferInformationMessage from '../displayDigitalOfferInformationMessage'

describe('src | components | pages | Offer | domain | getDurationInHours', () => {
  const bookType = {
    offlineOnly: false,
    onlineOnly: false,
    value: 'ThingType.LIVRE_EDITION',
  }

  const musicType = {
    offlineOnly: false,
    onlineOnly: false,
    value: 'ThingType.MUSIQUE',
  }

  const audioVisualType = {
    offlineOnly: false,
    onlineOnly: false,
    value: 'ThingType.AUDIOVISUEL',
  }

  const musicInstrumentType = {
    offlineOnly: true,
    onlineOnly: false,
    value: 'ThingType.INSTRUMENT',
  }

  const gameType = {
    offlineOnly: false,
    onlineOnly: true,
    value: 'ThingType.JEUX_VIDEO',
  }

  const virtualVenue = {
    isVirtual: true,
  }
  const physicalVenue = {
    isVirtual: false,
  }

  describe('when venue is digital', () => {
    describe('when offer type is a book', () => {
      it('should not display digital offer information message', () => {
        expect(displayDigitalOfferInformationMessage(bookType, virtualVenue)).toBe(false)
      })
    })
    describe('when offer type is available online or offline ', () => {
      it('should display digital offer information message', () => {
        expect(displayDigitalOfferInformationMessage(musicType, virtualVenue)).toBe(true)
      })
    })

    describe('when offer type is available online only', () => {
      it('should display digital offer information message', () => {
        expect(displayDigitalOfferInformationMessage(gameType, virtualVenue)).toBe(true)
      })
    })
  })

  describe('when venue is physical', () => {
    describe('when offer type is not digital at all', () => {
      it('should not display digital offer information message', () => {
        expect(displayDigitalOfferInformationMessage(musicInstrumentType, physicalVenue)).toBe(
          false
        )
      })
    })

    describe('when offer type is a book', () => {
      it('should not display digital offer information message', () => {
        expect(displayDigitalOfferInformationMessage(bookType, physicalVenue)).toBe(false)
      })
    })

    describe('when offer type is available online or offline', () => {
      it('should not display digital offer information message', () => {
        expect(displayDigitalOfferInformationMessage(audioVisualType, physicalVenue)).toBe(false)
      })
    })
  })

  describe('when no type', () => {
    it('should return false by defaut', () => {
      expect(displayDigitalOfferInformationMessage()).toBe(false)
    })
  })
})
