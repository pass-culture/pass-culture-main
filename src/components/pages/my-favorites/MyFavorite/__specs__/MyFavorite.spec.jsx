import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import MyFavorite from '../MyFavorite'

describe('src | components | pages | my-favorites | MyFavorite | MyFavorite', () => {
  let props

  beforeEach(() => {
    props = {
      detailsUrl: 'fake/url',
      favorite: {
        id: 'AE',
        thumbUrl: '',
      },
      humanizeRelativeDistance: '10 km',
      location: {
        pathname: '',
        search: '',
      },
      offer: {
        id: 'Fake id',
        name: 'Fake offer name',
        product: {
          offerType: {
            appLabel: 'Fake offer type label',
          },
        },
      },
      status: {
        label: 'Réservé',
        class: 'booked',
      },
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<MyFavorite {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a booking by default', () => {
    // when
    const wrapper = shallow(<MyFavorite {...props} />)

    // then
    const link = wrapper.find(Link)
    const img = wrapper.find('img')
    const title = wrapper.find('.teaser-title').text()
    const type = wrapper.find('.mf-wrapper > .teaser-sub-title').text()
    const booked = wrapper.find('.mf-booked').text()
    const distance = wrapper.find('.mf-infos .teaser-sub-title').text()
    expect(link).toHaveLength(1)
    expect(img).toHaveLength(0)
    expect(title).toBe('Fake offer name')
    expect(type).toBe('Fake offer type label')
    expect(booked).toBe('Réservé')
    expect(distance).toBe('10 km')
  })
})
