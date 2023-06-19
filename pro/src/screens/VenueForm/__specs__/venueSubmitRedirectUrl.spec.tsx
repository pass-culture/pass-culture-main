import {
  SharedCurrentUserResponseModel,
  VenueResponseModel,
} from 'apiClient/v1'

import { IOfferer } from '../../../core/Offerers/types'
import { venueSubmitRedirectUrl } from '../utils/venueSubmitRedirectUrl'

let useNewOfferCreationJourney: boolean

const offerer = { nonHumanizedId: 1 } as IOfferer
const venue = { id: 12 } as VenueResponseModel

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
          offerer.nonHumanizedId,
          venue.id,
          { isAdmin: true } as SharedCurrentUserResponseModel
        )

        expect(url).toEqual(`/structures/${offerer.nonHumanizedId}`)
      }
    )

    it('Redirect non admin user to the right url on creation', () => {
      const url = venueSubmitRedirectUrl(
        useNewOfferCreationJourney,
        true,
        offerer.nonHumanizedId,
        venue.id,
        { isAdmin: false } as SharedCurrentUserResponseModel
      )

      expect(url).toEqual('/accueil?success')
    })

    it('Redirect non admin user to the right url on update', () => {
      const url = venueSubmitRedirectUrl(
        useNewOfferCreationJourney,
        false,
        offerer.nonHumanizedId,
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
      offerer.nonHumanizedId,
      venue.id,
      { isAdmin: true } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual(
      `/structures/${offerer.nonHumanizedId}/lieux/${venue.id}`
    )
  })

  it('Redirect admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      false,
      offerer.nonHumanizedId,
      venue.id,
      { isAdmin: true } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual(`/structures/${offerer.nonHumanizedId}`)
  })

  it('Redirect non admin user to the right url on creation', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      true,
      offerer.nonHumanizedId,
      venue.id,
      { isAdmin: false } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual(
      `/structures/${offerer.nonHumanizedId}/lieux/${venue.id}`
    )
  })

  it('Redirect non admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(
      useNewOfferCreationJourney,
      false,
      offerer.nonHumanizedId,
      venue.id,
      { isAdmin: false } as SharedCurrentUserResponseModel
    )

    expect(url).toEqual('/accueil')
  })
})
