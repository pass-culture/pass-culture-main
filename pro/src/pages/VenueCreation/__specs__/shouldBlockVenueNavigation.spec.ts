import { SharedCurrentUserResponseModel } from 'apiClient/v1'

import { shouldBlockVenueNavigation } from '../VenueCreationForm'

const userAdmin = {
  isAdmin: true,
} as SharedCurrentUserResponseModel

const userPro = {
  isAdmin: false,
} as SharedCurrentUserResponseModel

const offererId = 1

const defaultLocation = {
  pathname: '/',
  search: '',
  hash: '',
  state: {},
  key: 'key',
}

const defaultShouldBlockNavigationInVenueProps = {
  isNewOfferCreationJourney: true,
  offererId: offererId,
  user: userAdmin,
  selectedOffererId: offererId,
}

describe('shouldBlockNavigation', () => {
  it('should not block when creating venue and being redirected for admin', () => {
    const nextLocation = {
      ...defaultLocation,
      pathname: `/structures/${offererId}`,
    }

    const shouldBlockNavigationInVenueProps = {
      ...defaultShouldBlockNavigationInVenueProps,
      user: userAdmin,
    }

    const result = shouldBlockVenueNavigation(
      shouldBlockNavigationInVenueProps
    )({ currentLocation: defaultLocation, nextLocation: nextLocation })

    expect(result).toBe(false)
  })

  it('should not block when creating venue and being redirected for pro user', () => {
    const nextLocation = {
      ...defaultLocation,
      pathname: '/accueil',
      search: '?success',
    }

    const shouldBlockNavigationInVenueProps = {
      ...defaultShouldBlockNavigationInVenueProps,
      user: userPro,
    }

    const result = shouldBlockVenueNavigation(
      shouldBlockNavigationInVenueProps
    )({ currentLocation: defaultLocation, nextLocation: nextLocation })

    expect(result).toBe(false)
  })

  it('should block in creation when going outside of form', () => {
    const nextLocation = {
      ...defaultLocation,
      pathname: '/otherLocation',
    }

    const result = shouldBlockVenueNavigation(
      defaultShouldBlockNavigationInVenueProps
    )({ currentLocation: defaultLocation, nextLocation: nextLocation })

    expect(result).toBe(true)
  })
})
