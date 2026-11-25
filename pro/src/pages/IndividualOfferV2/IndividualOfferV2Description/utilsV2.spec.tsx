import {
  ArtistType,
  DisplayableActivity,
  type OfferExtraDataV2,
  OfferStatus,
  VenueState,
} from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/constants'

import { DEFAULT_DESCRIPTION_FORM_VALUES } from './constants'
import { getFormV2ReadOnlyFields, getInitialValuesFromOfferV2 } from './utilsV2'

const venue = makeGetVenueResponseModel({ id: 1 })
const closedVenue = makeGetVenueResponseModel({
  id: 2,
  state: VenueState.CLOSED,
})
const museumVenue = makeGetVenueResponseModel({
  id: 3,
  activity: DisplayableActivity.MUSEUM,
})

const allFieldsExceptAccessibility = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

const synchronizedOffer = getIndividualOfferFactory({
  lastProvider: { name: 'Boost' },
})

describe('getFormV2ReadOnlyFields', () => {
  it('should make every field readonly when the venue is closed', () => {
    const result = getFormV2ReadOnlyFields(
      getIndividualOfferFactory(),
      closedVenue
    )

    expect(result).toStrictEqual([
      ...allFieldsExceptAccessibility,
      'accessibility',
    ])
  })

  it('should make every field readonly when the venue is closed even for a new offer draft', () => {
    const result = getFormV2ReadOnlyFields(null, closedVenue)

    expect(result).toStrictEqual([
      ...allFieldsExceptAccessibility,
      'accessibility',
    ])
  })

  it('should make every field readonly when the offerer is closed', () => {
    const result = getFormV2ReadOnlyFields(
      getIndividualOfferFactory(),
      makeGetVenueResponseModel({
        id: 4,
        managingOfferer: { ...venue.managingOfferer, isClosed: true },
      })
    )

    expect(result).toStrictEqual([
      ...allFieldsExceptAccessibility,
      'accessibility',
    ])
  })

  it('should not have readonly fields for a new offer draft', () => {
    const result = getFormV2ReadOnlyFields(null, venue)

    expect(result).toStrictEqual([])
  })

  it.each([OfferStatus.REJECTED, OfferStatus.PENDING])(
    'should make every field readonly when the offer is %s',
    (status) => {
      const result = getFormV2ReadOnlyFields(
        getIndividualOfferFactory({ status }),
        venue
      )

      expect(result).toStrictEqual([
        ...allFieldsExceptAccessibility,
        'accessibility',
      ])
    }
  )

  it('should make every field except accessibility and cultural outreach claim readonly when the offer is synchronized', () => {
    const result = getFormV2ReadOnlyFields(synchronizedOffer, venue)

    expect(result).toStrictEqual(
      allFieldsExceptAccessibility.filter(
        (field) => field !== 'hasCulturalOutreachClaim'
      )
    )
    expect(result).not.toContain('accessibility')
  })

  it('should also let name and description be edited when a synchronized offer belongs to a museum', () => {
    const result = getFormV2ReadOnlyFields(synchronizedOffer, museumVenue)

    expect(result).toStrictEqual(
      allFieldsExceptAccessibility.filter(
        (field) =>
          field !== 'name' &&
          field !== 'description' &&
          field !== 'hasCulturalOutreachClaim'
      )
    )
  })

  it('should not have readonly fields for an editable offer', () => {
    const result = getFormV2ReadOnlyFields(getIndividualOfferFactory(), venue)

    expect(result).toStrictEqual([])
  })
})

describe('getInitialValuesFromOfferV2', () => {
  it('should build the form values from the offer', () => {
    const offer = getIndividualOfferFactory({
      name: 'Festival de la Musique',
      description: 'Ancien festival annuel musical',
      durationMinutes: 90,
      hasCulturalOutreachClaim: true,
      visualDisabilityCompliant: true,
      extraData: {
        author: 'Boris Vian',
        gtl_id: 'a gtl id',
        performer: 'Marcel et son orchestre',
        showType: 'a showtype',
        showSubType: 'a showSubtype',
        speaker: 'Robert Smith',
        stageDirector: 'Bob Sinclar',
        visa: '123456789',
        ean: 'any ean',
      },
      artistOfferLinks: [],
    })

    const result = getInitialValuesFromOfferV2(offer)

    expect(result).toStrictEqual({
      ...DEFAULT_DESCRIPTION_FORM_VALUES,
      name: 'Festival de la Musique',
      description: 'Ancien festival annuel musical',
      durationMinutes: 90,
      hasCulturalOutreachClaim: true,
      visualDisabilityCompliant: true,
      extraData: {
        author: 'Boris Vian',
        gtl_id: 'a gtl id',
        performer: 'Marcel et son orchestre',
        showType: 'a showtype',
        showSubType: 'a showSubtype',
        speaker: 'Robert Smith',
        stageDirector: 'Bob Sinclar',
        visa: '123456789',
        ean: 'any ean',
      },
      artistOfferLinks: DEFAULT_DESCRIPTION_FORM_VALUES.artistOfferLinks,
    })
  })

  it('should fall back to default values when optional fields are missing', () => {
    const offer = getIndividualOfferFactory({
      description: null,
      durationMinutes: null,
      visualDisabilityCompliant: null,
      extraData: null,
    })

    const result = getInitialValuesFromOfferV2(offer)

    expect(result).toMatchObject({
      description: DEFAULT_DESCRIPTION_FORM_VALUES.description,
      durationMinutes: DEFAULT_DESCRIPTION_FORM_VALUES.durationMinutes,
      visualDisabilityCompliant: false,
      extraData: DEFAULT_DESCRIPTION_FORM_VALUES.extraData,
    })
  })

  it('should define every extra data field, keeping only the known ones', () => {
    const offer = getIndividualOfferFactory({
      extraData: {
        author: 'Boris Vian',
        unknownField: 'unknown',
      } as OfferExtraDataV2,
    })

    const result = getInitialValuesFromOfferV2(offer)

    expect(result.extraData).toStrictEqual({
      ...DEFAULT_DESCRIPTION_FORM_VALUES.extraData,
      author: 'Boris Vian',
    })
  })

  it('should complete artist offer links with the missing default artist types', () => {
    const offer = getIndividualOfferFactory({
      artistOfferLinks: [
        {
          artistId: '1',
          artistName: 'Marcel et son orchestre',
          artistType: ArtistType.PERFORMER,
        },
      ],
    })

    const result = getInitialValuesFromOfferV2(offer)

    expect(result.artistOfferLinks).toStrictEqual([
      {
        artistId: '1',
        artistName: 'Marcel et son orchestre',
        artistType: ArtistType.PERFORMER,
      },
      { artistId: null, artistName: '', artistType: ArtistType.AUTHOR },
      { artistId: null, artistName: '', artistType: ArtistType.STAGE_DIRECTOR },
    ])
  })
})
