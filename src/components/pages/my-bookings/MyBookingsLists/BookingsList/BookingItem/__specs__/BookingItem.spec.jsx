import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import BookingItem, { stringify } from '../BookingItem'
import Icon from '../../../../../../layout/Icon/Icon'
import Ribbon from '../../../../../../layout/Ribbon/Ribbon'

describe('src | components | pages | my-bookings | MyBookingsList | BookingList | BookingItem', () => {
  describe('stringify()', () => {
    it('should stringify and capitalize a date with a time zone', () => {
      // given
      const date = '2019-07-08T20:00:00Z'
      const timeZone = 'Europe/Paris'

      // when
      const stringifyDate = stringify(date)(timeZone)

      // then
      expect(stringifyDate).toBe('Lundi 08/07/2019 à 22:00')
    })
  })

  let props
  let thumbUrl
  let token

  beforeEach(() => {
    token = 'g9g9g9'
    thumbUrl = '/offers/AE'
    props = {
      booking: {
        id: 'AE',
        isCancelled: false,
        stock: {},
        token,
        thumbUrl,
      },
      location: {
        pathname: '/reservations',
        search: '?',
      },
      match: {
        params: {
          details: undefined,
        },
      },
      offer: {
        id: 'AE',
        product: {
          name: 'Fake offer name to much longuer',
          type: 'thing',
        },
        venue: {
          departementCode: '93',
        },
      },
      stock: { id: 'future stock 1', beginningDatetime: '2030-08-21T20:00:00Z' },
    }
  })

  it('should render a booking by default', () => {
    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const link = wrapper.find(Link)
    const img = wrapper.find('img')
    const stringifyDate = wrapper.find('.teaser-sub-title').text()
    const token = wrapper.find('.mb-token').text()
    const icon = wrapper.find(Icon)
    const ribbon = wrapper.find(Ribbon)
    expect(link).toHaveLength(1)
    expect(img).toHaveLength(1)
    expect(stringifyDate).toBe('Mercredi 21/08/2030 à 22:00')
    expect(token).toBe(token)
    expect(ribbon).toHaveLength(0)
    expect(icon).toHaveLength(1)
  })

  it('should render a booking with an image', () => {
    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const imgSource = wrapper.find('img').props().src
    expect(imgSource).toBe(thumbUrl)
  })

  it('should render a booking with a date', () => {
    // given
    props.stock.beginningDatetime = '2019-07-08T20:00:00Z'
    props.stock.endDatetime = '2019-07-08T23:00:00Z'

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const stringifyDate = wrapper.find('.teaser-sub-title').text()
    expect(stringifyDate).toBe('Lundi 08/07/2019 à 22:00')
  })

  it('should render a booking with a Ribbon', () => {
    // given
    props.ribbon = {
      label: 'Annulé',
      type: 'cancelled',
    }

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const ribbon = wrapper.find(Ribbon)
    expect(ribbon).toHaveLength(1)
  })
})
