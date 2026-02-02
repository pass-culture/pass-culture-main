import { ArtistType } from '@/apiClient/v1'

import {
  deSerializeDurationMinutes,
  serializeDetailsPatchData,
  serializeDetailsPostData,
  serializeDurationMinutes,
  serializeExtraData,
} from '../serializers'
import type { DetailsFormValues } from '../types'

describe('deSerializeDurationMinutes', () => {
  it('should correctly de serialize duration minutes', () => {
    expect(deSerializeDurationMinutes(0)).toStrictEqual('00:00')
    expect(deSerializeDurationMinutes(21)).toStrictEqual('00:21')
    expect(deSerializeDurationMinutes(183)).toStrictEqual('03:03')
    expect(deSerializeDurationMinutes(1838)).toStrictEqual('30:38')
  })
})

describe('serializeExtraData', () => {
  const formValuesBase: DetailsFormValues = {
    name: 'anything',
    description: 'anything',
    venueId: 'anything',
    categoryId: 'anything',
    subcategoryId: 'anything',
    showType: 'a showtype',
    showSubType: 'a showSubtype',
    gtl_id: 'a gtl id',
    author: 'Boris Vian',
    performer: 'Marcel et son orchestre',
    ean: 'any ean',
    speaker: 'Robert Smith',
    stageDirector: 'Bob Sinclar',
    visa: '123456789',
    durationMinutes: '',
    subcategoryConditionalFields: [],
    productId: '',
    artistOfferLinks: [],
  }

  it('should correctly serialize extra data without artistsOfferLinks', () => {
    expect(serializeExtraData(formValuesBase, false)).toStrictEqual({
      author: 'Boris Vian',
      ean: 'any ean',
      gtl_id: 'a gtl id',
      performer: 'Marcel et son orchestre',
      showSubType: 'a showSubtype',
      showType: 'a showtype',
      speaker: 'Robert Smith',
      stageDirector: 'Bob Sinclar',
      visa: '123456789',
    })
  })

  it('should correctly serialize extra data with artistsOfferLinks', () => {
    const formValues: DetailsFormValues = {
      ...formValuesBase,
      author: '',
      performer: '',
      stageDirector: '',
      artistOfferLinks: [
        {
          artistId: '1',
          artistName: 'Boris Vian',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          artistName: 'Aya Nakamura',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          artistName: 'Marcel et son orchestre',
          artistType: ArtistType.PERFORMER,
        },
        {
          artistId: '2',
          artistName: 'Bob Sinclar',
          artistType: ArtistType.STAGE_DIRECTOR,
        },
      ],
    }

    expect(serializeExtraData(formValues, true)).toStrictEqual({
      author: 'Boris Vian, Aya Nakamura',
      ean: 'any ean',
      gtl_id: 'a gtl id',
      performer: 'Marcel et son orchestre',
      showSubType: 'a showSubtype',
      showType: 'a showtype',
      speaker: 'Robert Smith',
      stageDirector: 'Bob Sinclar',
      visa: '123456789',
    })
  })

  it('should correctly serialize extra data with empty values', () => {
    const formValues: DetailsFormValues = {
      ...formValuesBase,
      name: '',
      description: '',
      venueId: '',
      categoryId: '',
      subcategoryId: '',
      showType: '',
      showSubType: '',
      gtl_id: '',
      author: '',
      performer: '',
      ean: '',
      speaker: '',
      stageDirector: '',
      visa: '',
    }

    expect(serializeExtraData(formValues, false)).toStrictEqual({
      author: null,
      ean: null,
      gtl_id: null,
      performer: null,
      showSubType: null,
      showType: null,
      speaker: null,
      stageDirector: null,
      visa: null,
    })
  })

  it('should correctly serialize extra data with productId', () => {
    const formValues: DetailsFormValues = {
      ...formValuesBase,
      productId: '123',
      artistOfferLinks: [
        {
          artistId: '1',
          artistName: 'Aya Nakamura',
          artistType: ArtistType.AUTHOR,
        },
      ],
    }

    expect(serializeExtraData(formValues, false)).toStrictEqual({
      author: 'Boris Vian',
      ean: 'any ean',
      gtl_id: 'a gtl id',
      performer: 'Marcel et son orchestre',
      showSubType: 'a showSubtype',
      showType: 'a showtype',
      speaker: 'Robert Smith',
      stageDirector: 'Bob Sinclar',
      visa: '123456789',
    })
  })
})

describe('serializeDetailsPostData', () => {
  const formValuesBase: DetailsFormValues = {
    name: ' Festival de la Musique ',
    description: ' Ancien festival annuel musical ',
    venueId: '0',
    categoryId: 'anything',
    subcategoryId: 'anything',
    showType: 'a showtype',
    showSubType: 'a showSubtype',
    gtl_id: 'a gtl id',
    author: ' Boris Vian ',
    performer: ' Marcel et son orchestre ',
    ean: ' any ean ',
    speaker: ' Robert Smith ',
    stageDirector: ' Bob Sinclar ',
    visa: ' 123456789 ',
    durationMinutes: '',
    subcategoryConditionalFields: [],
    productId: '',
    accessibility: {
      audio: true,
      mental: false,
      motor: true,
      visual: false,
      none: false,
    },
    artistOfferLinks: [],
  }

  it('should correctly serialize without artistsOfferLinks', () => {
    const result = serializeDetailsPostData(formValuesBase, false)

    expect(result).toStrictEqual({
      name: 'Festival de la Musique',
      subcategoryId: 'anything',
      venueId: 0,
      description: 'Ancien festival annuel musical',
      durationMinutes: null,
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
      productId: undefined,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: false,
      artistOfferLinks: [],
    })
  })

  it('should correctly serialize with artist offer links', () => {
    const formValues: DetailsFormValues = {
      ...formValuesBase,
      artistOfferLinks: [
        {
          artistId: '1',
          artistName: ' Boris Vian ',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          artistName: ' Marcel et son orchestre ',
          artistType: ArtistType.PERFORMER,
        },
        {
          artistId: '2',
          artistName: 'Bob Sinclar',
          artistType: ArtistType.STAGE_DIRECTOR,
        },
      ],
    }

    const result = serializeDetailsPostData(formValues, true)

    expect(result).toMatchObject({
      extraData: {
        author: 'Boris Vian',
        performer: 'Marcel et son orchestre',
        stageDirector: 'Bob Sinclar',
      },
      artistOfferLinks: [
        {
          artistId: '1',
          customName: null,
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          customName: 'Marcel et son orchestre',
          artistType: ArtistType.PERFORMER,
        },
        {
          artistId: '2',
          customName: null,
          artistType: ArtistType.STAGE_DIRECTOR,
        },
      ],
    })
  })
})

describe('serializeDetailsPatchData', () => {
  const formValuesBase: DetailsFormValues = {
    name: ' Festival de la Musique ',
    description: ' Ancien festival annuel musical ',
    venueId: '0',
    categoryId: 'anything',
    subcategoryId: 'anything',
    showType: 'a showtype',
    showSubType: 'a showSubtype',
    gtl_id: 'a gtl id',
    author: ' Boris Vian ',
    performer: ' Marcel et son orchestre ',
    ean: ' any ean ',
    speaker: ' Robert Smith ',
    stageDirector: ' Bob Sinclar ',
    visa: ' 123456789 ',
    durationMinutes: '',
    subcategoryConditionalFields: [],
    productId: '',
    accessibility: {
      audio: true,
      mental: false,
      motor: true,
      visual: false,
      none: false,
    },
    artistOfferLinks: [],
  }

  it('should correctly serialize without artistsOfferLinks', () => {
    const result = serializeDetailsPatchData(formValuesBase, false)

    expect(result).toStrictEqual({
      name: 'Festival de la Musique',
      subcategoryId: 'anything',
      description: 'Ancien festival annuel musical',
      durationMinutes: null,
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
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: false,
      artistOfferLinks: [],
    })
  })
  it('should correctly serialize artist offer links', () => {
    const formValues: DetailsFormValues = {
      ...formValuesBase,
      artistOfferLinks: [
        {
          artistId: '1',
          artistName: ' Boris Vian ',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          artistName: ' Marcel et son orchestre ',
          artistType: ArtistType.PERFORMER,
        },
        {
          artistId: '2',
          artistName: 'Bob Sinclar',
          artistType: ArtistType.STAGE_DIRECTOR,
        },
      ],
    }

    const result = serializeDetailsPatchData(formValues, true)

    expect(result).toMatchObject({
      extraData: {
        author: 'Boris Vian',
        performer: 'Marcel et son orchestre',
        stageDirector: 'Bob Sinclar',
      },
      artistOfferLinks: [
        {
          artistId: '1',
          customName: null,
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          customName: 'Marcel et son orchestre',
          artistType: ArtistType.PERFORMER,
        },
        {
          artistId: '2',
          customName: null,
          artistType: ArtistType.STAGE_DIRECTOR,
        },
      ],
    })
  })
})

describe('serializeDurationMinutes', () => {
  it('should return undefined when durationHour is empty', () => {
    expect(serializeDurationMinutes('')).toStrictEqual(null)
  })

  it('should transform string duration into int minutes', () => {
    expect(serializeDurationMinutes('0:00')).toStrictEqual(0)
    expect(serializeDurationMinutes('0:21')).toStrictEqual(21)
    expect(serializeDurationMinutes('3:03')).toStrictEqual(183)
    expect(serializeDurationMinutes('30:38')).toStrictEqual(1838)
  })
})
