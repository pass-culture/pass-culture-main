import {
  deSerializeDurationMinutes,
  serializeExtraData,
  serializeDetailsPostData,
  serializeDurationMinutes,
} from '../serializers'

describe('deSerializeDurationMinutes', () => {
  it('should correctly de serialize duration minutes', () => {
    expect(deSerializeDurationMinutes(0)).toStrictEqual('0:00')
    expect(deSerializeDurationMinutes(21)).toStrictEqual('0:21')
    expect(deSerializeDurationMinutes(183)).toStrictEqual('3:03')
    expect(deSerializeDurationMinutes(1838)).toStrictEqual('30:38')
  })
})

describe('serializeExtraData', () => {
  it('should correctly serialize extra data', () => {
    const formValues = {
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
    }

    expect(serializeExtraData(formValues)).toStrictEqual({
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

  it('should correctly serialize extra data with empty values', () => {
    const formValues = {
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
      durationMinutes: '',
      subcategoryConditionalFields: [],
      productId: '',
    }

    expect(serializeExtraData(formValues)).toStrictEqual({
      author: '',
      ean: '',
      gtl_id: '',
      performer: '',
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      visa: '',
    })
  })
})

describe('serializeDetailsPostData', () => {
  it('should trim spaces in all string fields', () => {
    const formValues = {
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
    }

    expect(serializeDetailsPostData(formValues)).toStrictEqual({
      name: 'Festival de la Musique',
      subcategoryId: 'anything',
      venueId: 0,
      description: 'Ancien festival annuel musical',
      durationMinutes: undefined,
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
      url: undefined,
      productId: undefined,
    })
  })
})

describe('serializeDurationMinutes', () => {
  it('should return undefined when durationHour is empty', () => {
    expect(serializeDurationMinutes('')).toStrictEqual(undefined)
  })

  it('should transform string duration into int minutes', () => {
    expect(serializeDurationMinutes('0:00')).toStrictEqual(0)
    expect(serializeDurationMinutes('0:21')).toStrictEqual(21)
    expect(serializeDurationMinutes('3:03')).toStrictEqual(183)
    expect(serializeDurationMinutes('30:38')).toStrictEqual(1838)
  })
})
