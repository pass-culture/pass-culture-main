import mockdate from 'mockdate'
import { shallow } from 'enzyme'
import React from 'react'

import Result from '../Result'

jest.mock('../../../../../../../utils/thumb', () => ({
  DEFAULT_THUMB_URL: '/default/thumb/url',
}))

jest.mock('../../../../../../../utils/config', () => ({
  OBJECT_STORAGE_URL: 'http://storage_path',
}))

describe('components | Result', () => {
  let props
  beforeAll(() => {
    mockdate.set(new Date(2020, 0, 1))
  })

  beforeEach(() => {
    props = {
      geolocation: {
        latitude: 42.2,
        longitude: 43.3,
      },
      result: {
        _geoloc: {
          lat: 2,
          lng: 5,
        },
        offer: {
          dates: [1585484866, 1585484866],
          id: 'AE',
          isDigital: false,
          subcategoryLabel: 'Livre',
          name: 'Les fleurs du mal',
          priceMin: 8,
          priceMax: 12,
          thumbUrl: '/thumbs/lien-vers-mon-image',
        },
        venue: {
          departementCode: '54',
        },
        objectID: '1',
      },
      search: '?mots-cles=librairie&page=1',
      searchGroupLabel: 'Livres',
    }
  })

  it('should render a Link component containing offer informations', () => {
    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerName = wrapper.findWhere(node => node.text() === 'Les fleurs du mal').first()
    const offerLabel = wrapper.findWhere(node => node.text() === 'Livres').first()
    const offerDate = wrapper.findWhere(node => node.text() === 'Dimanche 29 mars 14:27').first()
    const offerPrice = wrapper.findWhere(node => node.text() === 'À partir de 8 €').first()
    const offerDistance = wrapper.findWhere(node => node.text() === '900+ km').first()
    const offerMediation = wrapper.find('img')
    expect(wrapper.prop('to')).toBe('/recherche/resultats/details/AE?mots-cles=librairie&page=1')
    expect(offerName).toHaveLength(1)
    expect(offerLabel).toHaveLength(1)
    expect(offerDate).toHaveLength(1)
    expect(offerPrice).toHaveLength(1)
    expect(offerDistance).toHaveLength(1)
    expect(offerMediation).toHaveLength(1)
    expect(offerMediation.prop('src')).toBe('http://storage_path/thumbs/lien-vers-mon-image')
  })

  it('should render a Link component containing free offer when offer is free', () => {
    // given
    props.result.offer.priceMin = 0

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerPrice = wrapper.findWhere(node => node.text() === 'Gratuit').first()
    expect(offerPrice).toHaveLength(1)
  })

  it('should render a Link component containing offer price when offer has an unique price', () => {
    // given
    props.result.offer.priceMin = 5
    props.result.offer.priceMax = 5

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerPrice = wrapper.findWhere(node => node.text() === '5 €').first()
    expect(offerPrice).toHaveLength(1)
  })

  it('should render a Link component  not containing offer price when price is undefined', () => {
    // given
    props.result.offer.priceMin = undefined
    props.result.offer.priceMax = undefined

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerPrice = wrapper.findWhere(node => node.text() === 'undefined €').first()
    expect(offerPrice).toHaveLength(0)
  })

  it('should render a Link component with no date when no dates', () => {
    // given
    props.result.offer.dates = []

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerDate = wrapper.find('[data-test="result-date-test"]')
    expect(offerDate).toHaveLength(0)
  })

  it('should render a Link component with date when dates are provided', () => {
    // given
    props.result.offer.dates = [1595854599, 1595854599]

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerDate = wrapper.find('[data-test="result-date-test"]')
    expect(offerDate).toHaveLength(1)
  })

  it('should render a Link component with no distance when distance is not provided', () => {
    // given
    props.geolocation = {}

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerDate = wrapper.find('[data-test="result-distance-test"]')
    expect(offerDate).toHaveLength(0)
  })

  it('should render a Link component with no distance when the offer is digital', () => {
    // given
    props.result.offer.isDigital = true

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerDistance = wrapper.find('[data-test="result-distance-test"]')
    expect(offerDistance).toHaveLength(0)
  })

  it('should render default thumb if no thumb url is specified', () => {
    // given
    props.result.offer.thumbUrl = null

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerMediation = wrapper.find('img')
    expect(offerMediation.prop('src')).toBe('/default/thumb/url')
  })
})
