import { OfferAddressType } from 'apiClient/v1'
import { EVENT_ADDRESS_SCHOOL_LABEL } from 'screens/OfferEducational/constants/labels'
import { defaultGetVenue } from 'utils/collectiveApiFactories'

import { formatOfferEventAddress } from '../formatOfferEventAddress'

describe('formatOfferEventAddress', () => {
  it('when it is in offerer venue', () => {
    expect(
      formatOfferEventAddress(
        {
          addressType: OfferAddressType.OFFERER_VENUE,
          otherAddress: '',
          venueId: 12,
        },
        {
          ...defaultGetVenue,
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          street: '12 rue Duhesme',
        }
      )
    ).toBe('Offerer venue, 12 rue Duhesme, 75000, Paris')
  })

  it('when it is in the school', () => {
    expect(
      formatOfferEventAddress(
        {
          addressType: OfferAddressType.SCHOOL,
          otherAddress: '',
          venueId: null,
        },
        {
          ...defaultGetVenue,
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          street: '12 rue Duhesme',
        }
      )
    ).toBe(EVENT_ADDRESS_SCHOOL_LABEL)
  })

  it('when it is in another location', () => {
    expect(
      formatOfferEventAddress(
        {
          addressType: OfferAddressType.OTHER,
          otherAddress: 'A la mairie',
          venueId: 12,
        },
        {
          ...defaultGetVenue,
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          street: '12 rue Duhesme',
        }
      )
    ).toBe('A la mairie')
  })
})
