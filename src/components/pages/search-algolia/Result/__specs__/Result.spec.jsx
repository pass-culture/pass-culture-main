import { shallow } from 'enzyme'
import React from 'react'

import Result from '../Result'

jest.mock('../../../../../utils/thumb', () => ({
  DEFAULT_THUMB_URL: '/default/thumb/url',
}))

describe('components | Result', () => {
  let props

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
          departementCode: 54,
          id: 'AE',
          label: 'Livre',
          name: 'Les fleurs du mal',
          priceMin: 8,
          priceMax: 12,
          thumbUrl: '/lien-vers-mon-image',
        },
        objectID: 'AE',
      },
      search: '?mots-cles=librairie&page=1',
    }
  })

  it('should render a Link component containing offer informations', () => {
    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerName = wrapper.findWhere(node => node.text() === 'Les fleurs du mal').first()
    const offerLabel = wrapper.findWhere(node => node.text() === 'Livre').first()
    const offerDate = wrapper.findWhere(node => node.text() === 'dim. 29 mars 12:27').first()
    const offerPrice = wrapper.findWhere(node => node.text() === 'A partir de 8 €').first()
    const offerDistance = wrapper.findWhere(node => node.text() === '900+ km').first()
    const offerMediation = wrapper.find('img')
    expect(wrapper.prop('to')).toBe('/recherche-offres/resultats/details/AE?mots-cles=librairie&page=1')
    expect(offerName).toHaveLength(1)
    expect(offerLabel).toHaveLength(1)
    expect(offerDate).toHaveLength(1)
    expect(offerPrice).toHaveLength(1)
    expect(offerDistance).toHaveLength(1)
    expect(offerMediation).toHaveLength(1)
    expect(offerMediation.prop('src')).toBe('/lien-vers-mon-image')
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

  it('should render a Link component containing price offer when offer has an unique price', () => {
    // given
    props.result.offer.priceMin = 5
    props.result.offer.priceMax = 5

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerPrice = wrapper.findWhere(node => node.text() === '5 €').first()
    expect(offerPrice).toHaveLength(1)
  })

  it('should render a Link component containing with no date when no dates', () => {
    // given
    props.result.offer.dates = []

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerDate = wrapper.find('[data-test="result-date-test"]')
    expect(offerDate).toHaveLength(0)
  })

  it('should render a Link component containing with date when dates are provided', () => {
    // given
    props.result.offer.dates = [1595854599, 1595854599]

    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerDate = wrapper.find('[data-test="result-date-test"]')
    expect(offerDate).toHaveLength(1)
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
