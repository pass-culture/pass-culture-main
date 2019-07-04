import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import MyBooking from '../MyBooking'
import Icon from '../../../layout/Icon'
import Ribbon from '../../../layout/Ribbon'

describe('src | components | pages | my-bookings | MyBooking', () => {
  let props

  beforeEach(() => {
    props = {
      name: 'Fake booking to much longuer',
      offerVersoUrl: 'https://example.net/decouverte/ME/FA/verso',
      token: 'g9g9g9',
      type: 'thing',
    }
  })

  it('should render a booking by default', () => {
    // when
    const wrapper = shallow(<MyBooking {...props} />)

    // then
    const link = wrapper.find(Link)
    const img = wrapper.find('img')
    const stringifyDate = wrapper.find('.mb-date').text()
    const token = wrapper.find('.mb-token').text()
    const icon = wrapper.find(Icon)
    const ribbon = wrapper.find(Ribbon)
    expect(link).toHaveLength(1)
    expect(img).toHaveLength(0)
    expect(stringifyDate).toBe('Permanent')
    expect(token).toBe('g9g9g9')
    expect(ribbon).toHaveLength(0)
    expect(icon).toHaveLength(1)
  })

  it('should render a booking with an image', () => {
    // given
    props.thumbUrl = 'https://example.net/mediation/image'

    // when
    const wrapper = shallow(<MyBooking {...props} />)

    // then
    const imgSource = wrapper.find('img').props().src
    expect(imgSource).toBe('https://example.net/mediation/image')
  })

  it('should render a booking with a date', () => {
    // given
    props.stringifyDate = 'Lundi 08/07/2019 à 22:00'

    // when
    const wrapper = shallow(<MyBooking {...props} />)

    // then
    const stringifyDate = wrapper.find('.mb-date').text()
    expect(stringifyDate).toBe('Lundi 08/07/2019 à 22:00')
  })

  it('should render a booking with a Ribbon', () => {
    // given
    props.isCancelled = true

    // when
    const wrapper = shallow(<MyBooking {...props} />)

    // then
    const ribbon = wrapper.find(Ribbon)
    expect(ribbon).toHaveLength(1)
  })
})
