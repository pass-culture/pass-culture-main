import { OfferAddressType } from 'apiClient/v1'
import { IVenue } from 'core/Venue'
import { EVENT_ADDRESS_SCHOOL_LABEL } from 'screens/OfferEducational/constants/labels'

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
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          address: '12 rue Duhesme',
        } as IVenue
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
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          address: '12 rue Duhesme',
        } as IVenue
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
          name: 'Offerer venue',
          publicName: '',
          postalCode: '75000',
          city: 'Paris',
          address: '12 rue Duhesme',
        } as IVenue
      )
    ).toBe('A la mairie')
  })
})
