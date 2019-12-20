import { shallow } from 'enzyme'
import React from 'react'
import Result from '../Result'

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
          dateRange: ['2019-01-01', '2019-01-30'],
          departementCode: 54,
          id: 'AE',
          label: 'Livre',
          name: 'Les fleurs du mal',
          thumbUrl: '/lien-vers-mon-image',
        },
        objectID: 'AE',
      },
      search: '?mots-cles=librairie&page=1'
    }
  })

  it('should render a Link component containing offer informations', () => {
    // when
    const wrapper = shallow(<Result {...props} />)

    // then
    const offerName = wrapper.findWhere(node => node.text() ===  'Les fleurs du mal').first()
    const offerLabel = wrapper.findWhere(node => node.text() ===  'Livre').first()
    const offerDateRange = wrapper.findWhere(node => node.text() ===  'du 2019-1-1 au 2019-1-30').first()
    const offerDistance = wrapper.findWhere(node => node.text() ===  '5879 km').first()
    const offerMediation = wrapper.find('img')
    expect(wrapper.prop('to')).toBe('/recherche-algolia/details/AE?mots-cles=librairie&page=1')
    expect(offerName).toHaveLength(1)
    expect(offerLabel).toHaveLength(1)
    expect(offerDateRange).toHaveLength(1)
    expect(offerDistance).toHaveLength(1)
    expect(offerMediation).toHaveLength(1)
    expect(offerMediation.prop('src')).toBe('/lien-vers-mon-image')
  })
})
