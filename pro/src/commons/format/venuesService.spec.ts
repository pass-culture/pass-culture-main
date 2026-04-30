import { getLocationResponseModel } from '@/commons/utils/factories/commonOffersApiFactories'
import { offererAddressFactory } from '@/commons/utils/factories/offererAddressFactories'

import {
  computeAddressDisplayName,
  formatAndOrderAddresses,
} from './venuesService'

describe('formatAndOrderVenues', () => {
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
          value: offererAddress[1].id,
        },
        {
          label: 'Adresse - 1 Rue de paris 75001 Paris',
          value: offererAddress[0].id,
        },
      ])
    })
  })
})

describe('computeAddressDisplayName', () => {
  it('should format the address without the label', () => {
    const computedAddressDisplayName = computeAddressDisplayName(
      getLocationResponseModel({ label: undefined })
    )

    expect(computedAddressDisplayName).toBe('ma super rue 75008 city')
  })

  it('should format the address with the the label', () => {
    const computedAddressDisplayName = computeAddressDisplayName(
      getLocationResponseModel({ label: 'Mon Label' })
    )

    expect(computedAddressDisplayName).toBe(
      'Mon Label - ma super rue 75008 city'
    )
  })

  it('should format the address without the the label if `showAddress` is false', () => {
    const computedAddressDisplayName = computeAddressDisplayName(
      getLocationResponseModel({ label: 'Mon Label' }),
      false
    )

    expect(computedAddressDisplayName).toBe('ma super rue 75008 city')
  })
})
