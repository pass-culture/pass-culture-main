import userHasNoOffersInAPhysicalVenueYet from '../userHasNoOffersInAPhysicalVenueYet'

describe('src | components | pages | Offerers | utils | userHasNoOffersInAPhysicalVenueYet', () => {
  it('should return false if current user has offers and physical venues', () => {
    // given
    const currentUser = {
      hasOffers: true,
      hasPhysicalVenues: true
    }

    // when
    const result = userHasNoOffersInAPhysicalVenueYet(currentUser)

    // then
    expect(result).toBe(false)
  })

  it('should return true if current user has no offer but physical venues', () => {
    // given
    const currentUser = {
      hasOffers: false,
      hasPhysicalVenues: true
    }

    // when
    const result = userHasNoOffersInAPhysicalVenueYet(currentUser)

    // then
    expect(result).toBe(true)
  })

  it('should return true if current user has offers but no physical venue', () => {
    // given
    const currentUser = {
      hasOffers: true,
      hasPhysicalVenues: false
    }

    // when
    const result = userHasNoOffersInAPhysicalVenueYet(currentUser)

    // then
    expect(result).toBe(true)
  })

  it('should return true if current user has no offer and no physical venue', () => {
    // given
    const currentUser = {
      hasOffers: false,
      hasPhysicalVenues: false
    }

    // when
    const result = userHasNoOffersInAPhysicalVenueYet(currentUser)

    // then
    expect(result).toBe(true)
  })
})
