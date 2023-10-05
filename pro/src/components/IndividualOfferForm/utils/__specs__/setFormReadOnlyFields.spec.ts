import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_SOLD_OUT,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_DRAFT,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'

import { FORM_DEFAULT_VALUES } from '../../constants'
import setFormReadOnlyFields from '../setFormReadOnlyFields'

describe('setFormReadOnlyFields', () => {
  it('should return empty array when no offer is given', () => {
    const readOnlyFields = setFormReadOnlyFields(null)
    expect(readOnlyFields).toStrictEqual([])
  })

  const fullBlockedStatus = [OFFER_STATUS_PENDING, OFFER_STATUS_REJECTED]
  it.each(fullBlockedStatus)(
    'should return all form fields for %s offer status',
    async status => {
      const offer = {
        status,
      } as IndividualOffer
      const readOnlyFields = setFormReadOnlyFields(offer)
      expect(readOnlyFields.sort()).toStrictEqual(
        Object.keys(FORM_DEFAULT_VALUES).sort()
      )
    }
  )
  const blockedStatus = [
    OFFER_STATUS_ACTIVE,
    OFFER_STATUS_INACTIVE,
    OFFER_STATUS_SOLD_OUT,
    OFFER_STATUS_EXPIRED,
    OFFER_STATUS_DRAFT,
  ]
  it.each(blockedStatus)(
    'should return standard blocked field for %s offer status',
    async status => {
      const offer = {
        status,
      } as IndividualOffer
      const readOnlyFields = setFormReadOnlyFields(offer)
      expect(readOnlyFields).toStrictEqual([
        'categoryId',
        'subcategoryId',
        'offererId',
        'venueId',
      ])
    }
  )

  it('should allow edition of "isDuo" "accessibility" and "externalTicketOfficeUrl" for allocine sychronised offers', () => {
    const expectedReadOnlyFields = Object.keys(FORM_DEFAULT_VALUES).filter(
      (field: string) =>
        !['accessibility', 'externalTicketOfficeUrl', 'isDuo'].includes(field)
    )
    const offer = {
      lastProvider: {
        name: 'AlLocINé',
      },
    } as IndividualOffer
    const readOnlyFields = setFormReadOnlyFields(offer)
    expect(readOnlyFields.sort()).toStrictEqual(expectedReadOnlyFields.sort())
  })

  it('should allow edition of "accessibility" and "externalTicketOfficeUrl" for other sychronised offers', () => {
    const expectedReadOnlyFields = Object.keys(FORM_DEFAULT_VALUES).filter(
      (field: string) =>
        !['accessibility', 'externalTicketOfficeUrl'].includes(field)
    )
    const offer = {
      lastProvider: {
        name: 'AnySyncProviderName',
      },
    } as IndividualOffer
    const readOnlyFields = setFormReadOnlyFields(offer)
    expect(readOnlyFields.sort()).toStrictEqual(expectedReadOnlyFields.sort())
  })
})
