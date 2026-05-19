import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'

import { getUserDefaultPath } from '../getUserDefaultPath'

const setupStore = ({
  hasUser = false,
  hasVenueAssiociated = false,
  hasVenueOnboarded = false,
  hasVenueSelected = false,
  hasVenue = false,
}: {
  hasUser?: boolean
  hasVenueAssiociated?: boolean
  hasVenueOnboarded?: boolean
  hasVenueSelected?: boolean
  hasVenue?: boolean
}) => {
  const fakeVenue = makeVenueListItemLiteResponseModel({
    id: 101,
    managingOffererId: 100,
    name: 'Digital Venue A1',
  })
  const store = configureTestStore({
    user: {
      currentUser: hasUser ? sharedCurrentUserFactory() : null,
      selectedAdminOfferer: null,
      selectedPartnerVenue: hasVenueSelected
        ? makeGetVenueResponseModel({
            id: fakeVenue.id,
            isOnboarded: hasVenueOnboarded,
          })
        : null,
      venues: hasVenue ? [fakeVenue] : null,
      venuesWithPendingValidation:
        hasVenue && !hasVenueAssiociated ? [fakeVenue] : null,
    },
  })
  vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)
}

describe('getUserDefaultPath', () => {
  it('should return /connexion when user is not authenticated', () => {
    setupStore({ hasUser: false })

    expect(getUserDefaultPath()).toBe('/connexion')
  })

  it('should return /inscription/structure/recherche when user has no venues', () => {
    setupStore({ hasUser: true, hasVenue: false })

    expect(getUserDefaultPath()).toBe('/inscription/structure/recherche')
  })

  it('should return /hub when user has venues but no venue selected', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueSelected: false,
    })

    expect(getUserDefaultPath()).toBe('/hub')
  })

  it('should return /rattachement-en-cours when user has selected + non-associated venue', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueAssiociated: false,
      hasVenueSelected: true,
    })

    expect(getUserDefaultPath()).toBe('/rattachement-en-cours')
  })

  it('should return /onboarding when user has selected + non-onboarded venue', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueAssiociated: true,
      hasVenueOnboarded: false,
      hasVenueSelected: true,
    })

    expect(getUserDefaultPath()).toBe('/onboarding')
  })

  it('should return /accueil when user has selected + onboarded + associated venue', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueAssiociated: true,
      hasVenueOnboarded: true,
      hasVenueSelected: true,
    })

    expect(getUserDefaultPath()).toBe('/accueil')
  })
})
