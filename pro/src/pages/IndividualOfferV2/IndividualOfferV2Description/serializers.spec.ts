import { ArtistType, FormatEnum, NatureEnum } from '@/apiClient/v1'
import { EXTRA_DATA_FORM_FIELDS } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/constants'

import {
  serializeDescriptionPatchData,
  serializeDescriptionPostData,
} from './serializers'
import {
  type DescriptionFormInputValues,
  type DescriptionFormValues,
  getValidationSchema,
} from './validationSchemaV2'

const makeFormValues = (
  overrides: DescriptionFormInputValues = {}
): DescriptionFormValues =>
  getValidationSchema().parse({
    name: ' Festival de la Musique ',
    description: ' Ancien festival annuel musical ',
    durationMinutes: 90,
    hasCulturalOutreachClaim: false,
    visualDisabilityCompliant: true,
    artistOfferLinks: [],
    extraData: {
      author: ' Boris Vian ',
      gtl_id: 'a gtl id',
      performer: ' Marcel et son orchestre ',
      showType: 'a showtype',
      showSubType: 'a showSubtype',
      speaker: ' Robert Smith ',
      stageDirector: ' Bob Sinclar ',
      visa: ' 123456789 ',
      ean: ' any ean ',
    },
    ...overrides,
  })

const expectedExtraData = {
  author: 'Boris Vian',
  gtl_id: 'a gtl id',
  performer: 'Marcel et son orchestre',
  showType: 'a showtype',
  showSubType: 'a showSubtype',
  speaker: 'Robert Smith',
  stageDirector: 'Bob Sinclar',
  visa: '123456789',
  ean: 'any ean',
}

const artistOfferLinks = [
  {
    artistId: '1',
    artistName: ' Boris Vian ',
    artistType: ArtistType.AUTHOR,
  },
  {
    artistId: null,
    artistName: '   ',
    artistType: ArtistType.PERFORMER,
  },
  {
    artistId: '2',
    artistName: 'Bob Sinclar',
    artistType: ArtistType.STAGE_DIRECTOR,
  },
]

const expectedArtistOfferLinks = [
  { artistId: '1', artistName: 'Boris Vian', artistType: ArtistType.AUTHOR },
  {
    artistId: '2',
    artistName: 'Bob Sinclar',
    artistType: ArtistType.STAGE_DIRECTOR,
  },
]

describe('serializeDescriptionPostData', () => {
  it('should serialize and trim the form values', () => {
    const result = serializeDescriptionPostData(
      makeFormValues(),
      1,
      NatureEnum.BIEN,
      FormatEnum.LIVRE_PAPIER
    )

    expect(result).toStrictEqual({
      name: 'Festival de la Musique',
      venueId: 1,
      description: 'Ancien festival annuel musical',
      durationMinutes: 90,
      extraData: expectedExtraData,
      hasCulturalOutreachClaim: false,
      productId: null,
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: true,
      artistOfferLinks: [],
      nature: NatureEnum.BIEN,
      format: FormatEnum.LIVRE_PAPIER,
    })
  })

  it('should convert empty extra data values to null and omit missing ones', () => {
    const result = serializeDescriptionPostData(
      makeFormValues({
        extraData: { author: '', performer: '   ', ean: 'any ean' },
      }),
      1,
      NatureEnum.BIEN,
      FormatEnum.LIVRE_PAPIER
    )

    expect(result.extraData).toStrictEqual({
      author: null,
      performer: null,
      ean: 'any ean',
    })
  })

  it('should fall back to default values when optional fields are missing', () => {
    const result = serializeDescriptionPostData(
      getValidationSchema().parse({ artistOfferLinks: [] }),
      1,
      NatureEnum.BIEN,
      FormatEnum.LIVRE_PAPIER
    )

    expect(result).toMatchObject({
      name: '',
      description: null,
      extraData: {},
      hasCulturalOutreachClaim: null,
      visualDisabilityCompliant: false,
    })
  })

  it('should sanitize artist offer links', () => {
    const result = serializeDescriptionPostData(
      makeFormValues({ artistOfferLinks }),
      1,
      NatureEnum.BIEN,
      FormatEnum.LIVRE_PAPIER
    )

    expect(result.artistOfferLinks).toStrictEqual(expectedArtistOfferLinks)
  })
})

describe('serializeDescriptionPatchData', () => {
  it('should serialize and trim the form values', () => {
    const result = serializeDescriptionPatchData(makeFormValues())

    expect(result).toStrictEqual({
      name: 'Festival de la Musique',
      description: 'Ancien festival annuel musical',
      durationMinutes: 90,
      extraData: expectedExtraData,
      hasCulturalOutreachClaim: false,
      visualDisabilityCompliant: true,
      artistOfferLinks: [],
    })
  })

  it('should sanitize artist offer links', () => {
    const result = serializeDescriptionPatchData(
      makeFormValues({ artistOfferLinks })
    )

    expect(result.artistOfferLinks).toStrictEqual(expectedArtistOfferLinks)
  })

  it('should keep extra data when at least one extra data field is editable', () => {
    const result = serializeDescriptionPatchData(
      makeFormValues(),
      EXTRA_DATA_FORM_FIELDS.filter((field) => field !== 'ean')
    )

    expect(result.extraData).toStrictEqual(expectedExtraData)
  })

  it('should omit readonly fields', () => {
    const result = serializeDescriptionPatchData(makeFormValues(), [
      ...EXTRA_DATA_FORM_FIELDS,
      'durationMinutes',
      'hasCulturalOutreachClaim',
    ])

    expect(result).toStrictEqual({
      name: 'Festival de la Musique',
      description: 'Ancien festival annuel musical',
      visualDisabilityCompliant: true,
    })
  })
})
