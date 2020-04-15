import { selectTimezoneByVenueIdAndOffererId } from '../StockItemContainer'

describe('selectTimezoneByVenueIdAndOffererId', () => {
  const offererWithPhysicalVenue = {
    id: 'AE',
    postalCode: '97301',
  }
  const physicalVenue = {
    id: 'AE',
    isVirtual: false,
    departementCode: '973',
  }

  const offererWithVirtualVenue = {
    id: 'AF',
    postalCode: '93000',
  }
  const virtualVenue = {
    id: 'AF',
    isVirtual: true,
  }

  const state = {
    data: {
      offerers: [offererWithVirtualVenue, offererWithPhysicalVenue],
      venues: [physicalVenue, virtualVenue],
    },
  }

  it('should return undefined when no venue', () => {
    // given
    const venueId = 'not-valid-id'

    // when
    const result = selectTimezoneByVenueIdAndOffererId(state, venueId)

    // then
    expect(result).toBeUndefined()
  })

  it('should return undefined when virtual venue and no offerer', () => {
    // given
    const offererId = 'not-valid-id'
    const venueId = virtualVenue.id

    // when
    const result = selectTimezoneByVenueIdAndOffererId(state, venueId, offererId)

    // then
    expect(result).toBeUndefined()
  })

  it('should return the timezone of the venue when physical', () => {
    // given
    const venueId = physicalVenue.id

    // when
    const result = selectTimezoneByVenueIdAndOffererId(state, venueId)

    // then
    expect(result).toBe('America/Cayenne')
  })

  it('should return the timezone of the offerer when virtual', () => {
    // given
    state.data.offerers = [
      {
        id: 'AF',
        postalCode: '974',
      },
    ]
    const offererId = offererWithVirtualVenue.id
    const venueId = virtualVenue.id

    // when
    const result = selectTimezoneByVenueIdAndOffererId(state, venueId, offererId)

    // then
    expect(result).toBe('Indian/Reunion')
  })
})
