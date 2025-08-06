import { OfferAddressType } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererVenueResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { EVENT_ADDRESS_SCHOOL_LABEL } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/constants/labels'

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
        },
        []
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
        },
        []
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
        },
        []
      )
    ).toBe('A la mairie')
  })

  it('should use the offerer specific venue instead of the main venue', () => {
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
          id: 2,
        },
        [
          {
            ...defaultGetOffererVenueResponseModel,
            id: 12,
            name: 'Specific venue name',
          },
        ]
      )
    ).toContain('Specific venue name')
  })
})
