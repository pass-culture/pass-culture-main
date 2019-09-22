import buildOfferAltPictoByOfferType from '../buildOfferAltPictoByOfferType'

describe('src | components | layout | Verso | VersoHeader | utils | buildOfferAltPictoByOfferType', () => {
  it('should return an alternative name for the matching icon when offer type is provided and is AUDIOVISUEL', () => {
    // given
    const offerType = 'EventType.AUDIOVISUEL'

    // when
    const result = buildOfferAltPictoByOfferType(offerType)

    // then
    expect(result).toBe('audiovisuel')
  })

  it('should return an alternative name for the matching icon when offer type is provided and is SPECTACLE_VIVANT', () => {
    // given
    const offerType = 'EventType.SPECTACLE_VIVANT'

    // when
    const result = buildOfferAltPictoByOfferType(offerType)

    // then
    expect(result).toBe('spectacle vivant')
  })

  it('should return an alternative name for the matching icon when offer type is provided and is CONFERENCE_DEBAT_DEDICACE', () => {
    // given
    const offerType = 'EventType.CONFERENCE_DEBAT_DEDICACE'

    // when
    const result = buildOfferAltPictoByOfferType(offerType)

    // then
    expect(result).toBe('conference debat dedicace')
  })

  it('should return an alternative name for the matching icon when offer type is provided and includes multiple underscore', () => {
    // given
    const offerType = 'EventType.TEST_TEST_TEST_TEST'

    // when
    const result = buildOfferAltPictoByOfferType(offerType)

    // then
    expect(result).toBe('test test test test')
  })

  it('should return null when offer type is null', () => {
    // given
    const offerType = null

    // when
    const result = buildOfferAltPictoByOfferType(offerType)

    // then
    expect(result).toBeNull()
  })
})
