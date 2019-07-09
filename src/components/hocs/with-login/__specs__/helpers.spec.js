
import { getRedirectToOffersOrOfferers } from '../helpers'

describe('when the user is signin for the first time and has no offer and only a virtual venue created by default', () => {
  it('should redirect to offerers page', () => {
    // given
    const currentUser = {
      hasOffers: false,
      hasPhysicalVenues: false
    }

    // when
    const result = getRedirectToOffersOrOfferers({...currentUser})

    // then
    expect(result).toEqual("/structures")
  })
})

describe('when the user has a digital offer and only a virtual venue', () => {
  it('should redirect to offerers page', () => {
    // given
    const currentUser = {
      hasOffers: true,
      hasPhysicalVenues: false
    }

    // when
    const result = getRedirectToOffersOrOfferers({...currentUser})

    // then
    expect(result).toEqual("/structures")
  })
})

describe('when the user has no offers but a physical venue', () => {
  it('should redirect to offers page', () => {
    // given
    const currentUser = {
      hasOffers: false,
      hasPhysicalVenues: true
    }

    // when
    const result = getRedirectToOffersOrOfferers({...currentUser})

    // then
    expect(result).toEqual("/offres")
  })
})

describe('when the user has offers in physical venues', () => {
  it('should redirect to offers page', () => {
    // given
    const currentUser = {
      hasOffers: true,
      hasPhysicalVenues: true
    }

    // when
    const result = getRedirectToOffersOrOfferers({...currentUser})

    // then
    expect(result).toEqual("/offres")
  })
})
