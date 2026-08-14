import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { getOfferLastProvider } from '@/commons/utils/factories/providerFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { makeLocationFormValues } from '../../__mocks__/makeLocationFormValues'
import { toPatchOfferBodyModel } from '../toPatchOfferBodyModel'

vitest.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vitest.fn(),
}))

describe('toPatchOfferBodyModel', () => {
  const formValuesBase = makeLocationFormValues({
    location: {
      banId: '49759_1304_00002',
      city: 'Montpellier',
      inseeCode: '34172',
      isManualEdition: true,
      isVenueLocation: false,
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
    shouldSendMail: true,
  }

  it('should return empty object when offer is synchronized', () => {
    const offer = {
      ...offerBase,
      lastProvider: getOfferLastProvider(),
    }

    const result = toPatchOfferBodyModel({ ...paramsBase, offer })

    expect(result).toEqual({})
  })

  it('should return form values and shouldSendMail when offer is NOT synchronized', () => {
    const result = toPatchOfferBodyModel(paramsBase)

    expect(result).toEqual({
      location: {
        banId: '49759_1304_00002',
        city: 'Montpellier',
        inseeCode: '34172',
        isManualEdition: true,
        isVenueLocation: false,
        label: 'Centre commercial',
        latitude: '43.609296',
        longitude: '3.882445',
        postalCode: '34000',
        street: '79 Quai du Palladium',
      },
      url: 'https://example.org/page',
      shouldSendMail: true,
    })
  })

  it('should only send the flag when the venue address is selected', () => {
    const formValues = makeLocationFormValues({
      location: { ...formValuesBase.location, isVenueLocation: true },
      url: null,
    })

    const result = toPatchOfferBodyModel({ ...paramsBase, formValues })

    expect(result.location).toEqual({ isVenueLocation: true })
  })

  it('should forward null location fields as null', () => {
    const formValues = makeLocationFormValues({
      location: {
        ...formValuesBase.location,
        banId: null,
        inseeCode: null,
        label: null,
      },
      url: 'https://example.org/page',
    })

    const result = toPatchOfferBodyModel({ ...paramsBase, formValues })

    expect(result.location).toMatchObject({
      banId: null,
      inseeCode: null,
      label: null,
      city: 'Montpellier',
    })
  })

  it('should omit location when there is none', () => {
    const formValues = makeLocationFormValues({
      url: 'https://example.org/page',
    })

    const result = toPatchOfferBodyModel({ ...paramsBase, formValues })

    expect(result).not.toHaveProperty('location')
    expect(result).toHaveProperty('url', 'https://example.org/page')
  })

  it('should omit null top-level fields (url is null)', () => {
    const formValues = makeLocationFormValues({
      location: formValuesBase.location,
      url: null,
    })

    const result = toPatchOfferBodyModel({
      ...paramsBase,
      formValues,
      shouldSendMail: false,
    })

    expect(result).not.toHaveProperty('url')
    expect(result).toHaveProperty('location')
    expect(result.shouldSendMail).toBe(false)
  })

  it('should throw rather than post an address without a street', () => {
    // the validation schema requires `street` for `OTHER_ADDRESS`
    const formValues = makeLocationFormValues({
      location: { ...formValuesBase.location, street: null },
      url: null,
    })

    expect(() => toPatchOfferBodyModel({ ...paramsBase, formValues })).toThrow(
      '`location.street` is null'
    )
  })
})
