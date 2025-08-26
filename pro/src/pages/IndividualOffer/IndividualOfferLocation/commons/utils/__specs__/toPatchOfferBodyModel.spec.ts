import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { getOfferLastProvider } from '@/commons/utils/factories/providerFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { makeLocationFormValues } from '../../__mocks__/makeLocationFormValues'
import { toPatchOfferBodyModel } from '../toPatchOfferBodyModel'

describe('toPatchOfferBodyModel', () => {
  const formValuesBase = makeLocationFormValues({
    address: {
      banId: '49759_1304_00002',
      city: 'Montpellier',
      inseeCode: '34172',
      isManualEdition: true,
      isVenueAddress: false,
      label: 'Centre commercial',
      latitude: '43.609296',
      longitude: '3.882445',
      offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
      postalCode: '34000',
      street: '79 Quai du Palladium',
      addressAutocomplete: '79 Quai du Palladium 34000 Montpellier',
      coords: '43.609296, 3.882445',
      'search-addressAutocomplete': '79 Quai du Palladium 34000 Montpellier',
    },
    url: 'https://example.org/page',
  })
  const offerBase = getIndividualOfferFactory({})

  const paramsBase = {
    offer: offerBase,
    formValues: formValuesBase,
    shouldSendWarningMail: true,
  }

  it('should return empty object when offer is synchronized', () => {
    const offer = {
      ...offerBase,
      lastProvider: getOfferLastProvider(),
    }

    const result = toPatchOfferBodyModel({ ...paramsBase, offer })

    expect(result).toEqual({})
  })

  it('should return form values and shouldSendWarningMail when offer is NOT synchronized', () => {
    const offer = {
      ...offerBase,
      lastProvider: null,
    }

    const result = toPatchOfferBodyModel({ ...paramsBase, offer })

    expect(result).toMatchObject(formValuesBase)
    expect(result.shouldSendMail).toBe(true)
  })
})
