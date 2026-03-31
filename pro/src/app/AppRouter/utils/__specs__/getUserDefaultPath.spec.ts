import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'

import { getUserDefaultPath } from '../getUserDefaultPath'

const setupStore = (options: {
  access?: UserAccess | null
  hasUser?: boolean
  hasVenueSelected?: boolean
  hasVenue?: boolean
}) => {
  const store = configureTestStore({
    features: {
      list: [{ id: 1, isActive: true, name: 'WIP_SWITCH_VENUE' }],
    },
    user: {
      access: options.access ?? null,
      currentUser: options.hasUser ? sharedCurrentUserFactory() : null,
      selectedAdminOfferer: null,
      selectedPartnerVenue: options.hasVenueSelected
        ? makeGetVenueResponseModel({ id: 1 })
        : null,
      venues: options.hasVenue
        ? [
            makeVenueListItemLiteResponseModel({
              id: 3,
              managingOffererId: 1,
              name: 'Digital Venue A1',
            }),
          ]
        : null,
      venuesWithPendingValidation: null,
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
    setupStore({ hasUser: true, hasVenue: true, hasVenueSelected: false })

    expect(getUserDefaultPath()).toBe('/hub')
  })

  it('should return /rattachement-en-cours when selected venue is unattached', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueSelected: true,
      access: 'unattached',
    })

    expect(getUserDefaultPath()).toBe('/rattachement-en-cours')
  })

  it('should return /onboarding when user is not onboarded', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueSelected: true,
      access: 'no-onboarding',
    })

    expect(getUserDefaultPath()).toBe('/onboarding')
  })

  it('should return /accueil when user has full access', () => {
    setupStore({
      hasUser: true,
      hasVenue: true,
      hasVenueSelected: true,
      access: 'full',
    })

    expect(getUserDefaultPath()).toBe('/accueil')
  })
})
