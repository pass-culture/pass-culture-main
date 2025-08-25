import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { makeLocationFormValues } from '../../__mocks__/makeLocationFormValues'
import {
  isPhysicalLocationComplete,
  toPatchOfferBodyModel,
} from '../toPatchOfferBodyModel'

vi.mock('@/commons/core/Offers/utils/typology', () => ({
  isOfferSynchronized: vi.fn(),
}))

describe('toPatchOfferBodyModel', () => {
  const completeFormValues = makeLocationFormValues({
    banId: '49759_1304_00002',
    city: '"Montpellier"',
    inseeCode: '34172',
    isManualEdition: true,
    offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
    locationLabel: 'Centre commercial',
    latitude: '43.609296',
    longitude: '3.882445',
    postalCode: '34000',
    street: '"79 Quai du Palladium"',
    url: 'https://example.org/page',
  })

  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(isOfferSynchronized).mockReturnValue(false)
  })

  it('returns empty object when offer is synchronized', () => {
    vi.mocked(isOfferSynchronized).mockReturnValue(true)

    const offer = getIndividualOfferFactory({ isDigital: false })

    const result = toPatchOfferBodyModel({
      offer,
      formValues: completeFormValues,
      shouldSendWarningMail: true,
    })

    expect(result).toEqual({})
  })

  it('builds address when offer is not digital and form is complete (with trimming and quote removal)', () => {
    const offer = getIndividualOfferFactory({ isDigital: false })
    const formValues = {
      ...completeFormValues,
      offerLocation: OFFER_LOCATION.OTHER_ADDRESS, // should set isVenueAddress = false
    }

    const result = toPatchOfferBodyModel({
      offer,
      formValues,
      shouldSendWarningMail: true,
    })

    expect(result).toEqual({
      address: {
        banId: '49759_1304_00002',
        city: 'Montpellier',
        inseeCode: '34172',
        isManualEdition: true,
        isVenueAddress: false,
        label: 'Centre commercial',
        latitude: '43.609296',
        longitude: '3.882445',
        postalCode: '34000',
        street: '79 Quai du Palladium',
      },
      shouldSendMail: true,
      url: 'https://example.org/page',
    })
  })

  it('sets isVenueAddress = true when offerLocation is not OTHER_ADDRESS', () => {
    const offer = getIndividualOfferFactory({ isDigital: false })
    const formValues = {
      ...completeFormValues,
      offerLocation: 'VENUE_ADDRESS',
    }

    const result = toPatchOfferBodyModel({
      offer,
      formValues,
      shouldSendWarningMail: false,
    })

    expect(result.address).toBeTruthy()
    // AddressBodyModel allows isVenueAddress optional boolean; ensure it's true when not OTHER_ADDRESS
    expect(
      result.address && 'isVenueAddress' in result.address
        ? result.address.isVenueAddress
        : undefined
    ).toBe(true)
    expect(result.shouldSendMail).toBe(false)
  })

  it('should not return an when offer is digital even with complete form', () => {
    const offer = getIndividualOfferFactory({ isDigital: true })

    const result = toPatchOfferBodyModel({
      offer,
      formValues: completeFormValues,
      shouldSendWarningMail: true,
    })

    expect(result).not.toHaveProperty('address')
    expect(result.shouldSendMail).toBe(true)
    expect(result.url).toBe('https://example.org/page')
  })

  it('removes straight and fancy quotes from city and street', () => {
    const offer = getIndividualOfferFactory({ isDigital: false })

    const formValues = makeLocationFormValues({
      ...completeFormValues,
      city: '“Montpellier”',
      street: '«79 Quai du Palladium»',
    })

    const result = toPatchOfferBodyModel({
      offer,
      formValues,
      shouldSendWarningMail: false,
    })

    expect(result.address).toMatchObject({
      city: 'Montpellier',
      street: '79 Quai du Palladium',
    })
  })

  it.each([
    ['city', ''],
    ['latitude', ''],
    ['longitude', ''],
    ['postalCode', ''],
    ['street', ''],
    ['offerLocation', undefined], // must be truthy
  ] as const)(
    'should not return an address when required field %s is missing/falsy',
    (missingKey, missingValue) => {
      const offer = getIndividualOfferFactory({ isDigital: false })
      const formValues = {
        ...completeFormValues,
        [missingKey]: missingValue,
      }

      const result = toPatchOfferBodyModel({
        offer,
        formValues,
        shouldSendWarningMail: false,
      })

      expect(result).not.toHaveProperty('address')
      expect(result.url).toBe('https://example.org/page')
      expect(result.shouldSendMail).toBe(false)
    }
  )
})

describe('isPhysicalLocationComplete', () => {
  const completeFormValues = makeLocationFormValues({
    banId: ' 49759_1304_00002 ',
    city: ' "Montpellier" ',
    inseeCode: '34172',
    isManualEdition: true,
    offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
    locationLabel: ' Centre commercial ',
    latitude: ' 43.609296 ',
    longitude: ' 3.882445 ',
    postalCode: ' 34000 ',
    street: ' "79 Quai du Palladium" ',
    url: ' https://example.org/page ',
  })

  it('returns true when all required fields are truthy', () => {
    expect(isPhysicalLocationComplete(completeFormValues)).toBe(true)
  })

  it.each([
    ['city', null],
    ['latitude', null],
    ['longitude', null],
    ['postalCode', null],
    ['street', null],
    ['offerLocation', null],
  ] as const)(
    'returns false when required field %s is missing',
    (missingKey, missingValue) => {
      const formValues = {
        ...completeFormValues,
        [missingKey]: missingValue,
      }

      expect(isPhysicalLocationComplete(formValues)).toBe(false)
    }
  )
})
