import {
  GetCollectiveOfferVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { EVENT_ADDRESS_SCHOOL_LABEL } from 'screens/OfferEducational/constants/labels'

import { formatOfferEventAddress } from '../formatOfferEventAddress'

describe('formatOfferEventAddress', () => {
  it('when it is in offerer venue', () => {
    expect(
      formatOfferEventAddress(
        {
          addressType: OfferAddressType.OFFERER_VENUE,
          otherAddress: '',
          venueId: 'A1',
        },
        {
          id: 'A1',
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          address: '12 rue Duhesme',
        } as GetCollectiveOfferVenueResponseModel
      )
    ).toBe('Offerer venue, 12 rue Duhesme, 75000, Paris')
  })

  it('when it is in the school', () => {
    expect(
      formatOfferEventAddress(
        {
          addressType: OfferAddressType.SCHOOL,
          otherAddress: '',
          venueId: '',
        },
        {
          id: 'A1',
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          address: '12 rue Duhesme',
        } as GetCollectiveOfferVenueResponseModel
      )
    ).toBe(EVENT_ADDRESS_SCHOOL_LABEL)
  })

  it('when it is in another location', () => {
    expect(
      formatOfferEventAddress(
        {
          addressType: OfferAddressType.OTHER,
          otherAddress: 'A la mairie',
          venueId: '',
        },
        {
          id: 'A1',
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          address: '12 rue Duhesme',
        } as GetCollectiveOfferVenueResponseModel
      )
    ).toBe('A la mairie')
  })
})
