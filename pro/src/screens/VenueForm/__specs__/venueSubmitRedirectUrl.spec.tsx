import '@testing-library/jest-dom'

import {
  SharedCurrentUserResponseModel,
  VenueResponseModel,
} from 'apiClient/v1'

import { IOfferer } from '../../../core/Offerers/types'
import { venueSubmitRedirectUrl } from '../utils/venueSubmitRedirectUrl'

let useNewOfferCreationJourney: boolean

const offerer = { id: 'OF' } as IOfferer
const venue = { id: 'VN' } as VenueResponseModel

describe('redirect url after submit', () => {
  beforeEach(() => {
    useNewOfferCreationJourney = false
  })

  describe('With new journey', () => {
    beforeEach(() => {
      useNewOfferCreationJourney = true
    })

    it.each([true, false])(
      `Redirect admin user to the right url, when creation is %s`,
      creationMode => {
        const url = venueSubmitRedirectUrl(
          useNewOfferCreationJourney,
          creationMode,
          offerer.id,
          venue.id,
          { isAdmin: true } as SharedCurrentUserResponseModel
        )

        expect(url).toEqual('/structures/OF')
      }
    )

    it('Redirect non admin user to the right url on creation', () => {
      const url = venueSubmitRedirectUrl(
        useNewOfferCreationJourney,
        true,
        offerer.id,
        venue.id,
        { isAdmin: false } as SharedCurrentUserResponseModel
      )

      expect(url).toEqual('/accueil?success')
    })

    it('Redirect non admin user to the right url on update', () => {
      const url = venueSubmitRedirectUrl(
        useNewOfferCreationJourney,
        false,
        offerer.id,
        venue.id,
        { isAdmin: false } as SharedCurrentUserResponseModel
      )

      expect(url).toEqual('/accueil')
    })
  })

  it('Redirect admin user to the right url on creation', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      true,
      offerer.id,
      venue.id,
      { isAdmin: true } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual('/structures/OF/lieux/VN')
  })

  it('Redirect admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      false,
      offerer.id,
      venue.id,
      { isAdmin: true } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual('/structures/OF')
  })

  it('Redirect non admin user to the right url on creation', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      true,
      offerer.id,
      venue.id,
      { isAdmin: false } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual('/structures/OF/lieux/VN')
  })

  it('Redirect non admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      false,
      offerer.id,
      venue.id,
      { isAdmin: false } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual('/accueil')
  })
})
