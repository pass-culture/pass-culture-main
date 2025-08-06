import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
import { venueListItemFactory } from '@/commons/utils/factories/individualApiFactories'
import { offererAddressFactory } from '@/commons/utils/factories/offererAddressFactories'

import {
  computeAddressDisplayName,
  computeVenueDisplayName,
  formatAndOrderAddresses,
  formatAndOrderVenues,
} from '../venuesService'

describe('formatAndOrderVenues', () => {
  it('should sort venues alphabetically', () => {
    const venues = [
      venueListItemFactory({
        id: 1,
        name: 'Offre numérique',
        offererName: 'gilbert Joseph',
        isVirtual: true,
      }),
      venueListItemFactory({
        id: 1,
        name: 'a venue name',
        publicName: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        isVirtual: false,
      }),
    ]

    const sortingValues = formatAndOrderVenues(venues)

    expect(sortingValues).toStrictEqual([
      {
        label: 'gilbert Joseph - Offre numérique',
        value: venues[1].id.toString(),
      },
      {
        label: 'Librairie Fnac',
        value: venues[0].id.toString(),
      },
    ])
  })

  describe('formatAndOrderAddresses', () => {
    it('should sort offerer addresses alphabetically', () => {
      const offererAddress = [
        offererAddressFactory({
          label: 'Adresse',
        }),
        offererAddressFactory({
          street: '2 rue de Montreuil',
        }),
      ]

      const sortingValues = formatAndOrderAddresses(offererAddress)

      expect(sortingValues).toStrictEqual([
        {
          label: '2 rue de Montreuil 75001 Paris',
          value: offererAddress[1].id.toString(),
        },
        {
          label: 'Adresse - 1 Rue de paris 75001 Paris',
          value: offererAddress[0].id.toString(),
        },
      ])
    })
  })
})

describe('computeVenueDisplayName', () => {
  it('should give venue name when venue is not virtual and has no public name', () => {
    const venue = {
      id: 12,
      name: 'Librairie Fnac',
      offererName: 'gilbert Joseph',
      isVirtual: false,
    }

    const computedVenueDisplayName = computeVenueDisplayName(venue)

    expect(computedVenueDisplayName).toBe('Librairie Fnac')
  })

  it('should give venue public name when venue is not virtual and has a public name', () => {
    const venue = {
      id: 12,
      name: 'Librairie Fnac',
      offererName: 'gilbert Joseph',
      publicName: 'Ma petite librairie',
      isVirtual: false,
    }

    const computedVenueDisplayName = computeVenueDisplayName(venue)

    expect(computedVenueDisplayName).toBe('Ma petite librairie')
  })

  it('should give the offerer name with "- Offre numérique" when venue is virtual', () => {
    const venue = {
      id: 12,
      name: 'Librairie Fnac',
      offererName: 'gilbert Joseph',
      isVirtual: true,
    }

    const computedVenueDisplayName = computeVenueDisplayName(venue)

    expect(computedVenueDisplayName).toBe('gilbert Joseph - Offre numérique')
  })
})

describe('computeAddressDisplayName', () => {
  it('should format the address without the label', () => {
    const computedAddressDisplayName = computeAddressDisplayName(
      getAddressResponseIsLinkedToVenueModelFactory({ label: undefined })
    )

    expect(computedAddressDisplayName).toBe('ma super rue 75008 city')
  })

  it('should format the address with the the label', () => {
    const computedAddressDisplayName = computeAddressDisplayName(
      getAddressResponseIsLinkedToVenueModelFactory({ label: 'Mon Label' })
    )

    expect(computedAddressDisplayName).toBe(
      'Mon Label - ma super rue 75008 city'
    )
  })

  it('should format the address without the the label if `showAddress` is false', () => {
    const computedAddressDisplayName = computeAddressDisplayName(
      getAddressResponseIsLinkedToVenueModelFactory({ label: 'Mon Label' }),
      false
    )

    expect(computedAddressDisplayName).toBe('ma super rue 75008 city')
  })
})
