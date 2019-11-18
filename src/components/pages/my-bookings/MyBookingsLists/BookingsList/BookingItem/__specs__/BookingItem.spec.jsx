import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import BookingItem from '../BookingItem'
import Icon from '../../../../../../layout/Icon/Icon'
import Ribbon from '../../../../../../layout/Ribbon/Ribbon'
import { DEFAULT_THUMB_URL } from '../../../../../../../utils/thumb'

describe('src | components | pages | my-bookings | MyBookingsList | BookingList | BookingItem', () => {
  let props

  beforeEach(() => {
    props = {
      booking: {
        id: 'AE',
        isCancelled: false,
        qrCode: 'data:image/png;base64,iVIVhzdjeizfjezfoizejojczez',
        stock: {},
        token: 'G9G9G9',
        thumbUrl: '/mediations/AE',
      },
      isQrCodeFeatureDisabled: true,
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
        name: 'Un livre pas mal',
        product: {
          name: 'Un livre pas mal',
          type: 'thing',
        },
        venue: {
          departementCode: '93',
        },
      },
      stock: { id: 'future stock 1', beginningDatetime: '2030-08-21T20:00:00Z' },
      trackConsultOffer: jest.fn(),
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a booking including token when qr code feature is inactive', () => {
    // given
    props.isQrCodeFeatureDisabled = true

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingLink = wrapper.find(Link).first()
    const bookingThumb = wrapper.find('.teaser-thumb').find('img')
    const bookingName = wrapper.find('.teaser-title-booking')
    const bookingDate = wrapper.find('.teaser-sub-title')
    const bookingToken = wrapper.find('.mb-token-flipped')
    const arrowIcon = wrapper.find('.teaser-arrow').find(Icon)
    const ribbon = wrapper.find('.teaser-arrow').find(Ribbon)

    expect(bookingLink).toHaveLength(1)
    expect(bookingLink.prop('to')).toBe('/reservations/details/AE?')
    expect(bookingThumb).toHaveLength(1)
    expect(bookingThumb.prop('alt')).toBe('')
    expect(bookingThumb.prop('src')).toBe('/mediations/AE')
    expect(bookingName.text()).toBe('Un livre pas mal')
    expect(bookingDate.text()).toBe('Mercredi 21/08/2030 à 22:00')
    expect(bookingToken).toHaveLength(1)
    expect(bookingToken.text()).toBe('g9g9g9')
    expect(ribbon).toHaveLength(0)
    expect(arrowIcon).toHaveLength(1)
  })

  it('should render a booking with no token when qr code feature is active', () => {
    // given
    props.isQrCodeFeatureDisabled = false

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingLink = wrapper.find(Link).first()
    const bookingThumb = wrapper.find('.teaser-thumb').find('img')
    const bookingName = wrapper.find('.teaser-title-booking')
    const bookingDate = wrapper.find('.teaser-sub-title')
    const bookingToken = wrapper.find('.mb-token-flipped')
    const arrowIcon = wrapper.find('.teaser-arrow').find(Icon)
    const ribbon = wrapper.find('.teaser-arrow').find(Ribbon)

    expect(bookingLink).toHaveLength(1)
    expect(bookingLink.prop('to')).toBe('/reservations/details/AE?')
    expect(bookingThumb).toHaveLength(1)
    expect(bookingThumb.prop('alt')).toBe('')
    expect(bookingThumb.prop('src')).toBe('/mediations/AE')
    expect(bookingName.text()).toBe('Un livre pas mal')
    expect(bookingDate.text()).toBe('Mercredi 21/08/2030 à 22:00')
    expect(bookingToken).toHaveLength(0)
    expect(ribbon).toHaveLength(0)
    expect(arrowIcon).toHaveLength(1)
    expect(arrowIcon.prop('svg')).toBe('ico-next-S')
  })

  it('should render a booking with a date when its an event', () => {
    // given
    props.stock.beginningDatetime = '2019-07-08T20:00:00Z'
    props.stock.endDatetime = '2019-07-08T23:00:00Z'

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingDate = wrapper.find('.teaser-sub-title').text()
    expect(bookingDate).toBe('Lundi 08/07/2019 à 22:00')
  })

  it('should render a booking with no date when its not an event', () => {
    // given
    props.stock.beginningDatetime = null
    props.stock.endDatetime = null

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingDate = wrapper.find('.teaser-sub-title').text()
    expect(bookingDate).toBe('Permanent')
  })

  it('should render a booking with a thumb url on thumb when mediation is provided', () => {
    // given
    props.booking.thumbUrl = '/mediations/AE'

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingThumb = wrapper.find('.teaser-thumb').find('img')
    expect(bookingThumb.prop('src')).toBe('/mediations/AE')
  })

  it('should render a booking with a default thumb url on thumb when no mediation is provided', () => {
    // given
    props.booking.thumbUrl = null

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingThumb = wrapper.find('.teaser-thumb').find('img')
    expect(bookingThumb.prop('src')).toBe(DEFAULT_THUMB_URL)
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

  it('should render a link to booking qr code when offer is not used and qr code feature is active', () => {
    // given
    props.isQrCodeFeatureDisabled = false
    props.booking.qrCode = 'data:image/png;base64,iVIVhzdjeizfjezfoizejojczez'

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingTokenLink = wrapper.find('.mb-token-container').find(Link)
    expect(bookingTokenLink).toHaveLength(1)
    expect(bookingTokenLink.prop('to')).toBe('/reservations/details/AE?/qrcode')
  })

  it('should not render a link to booking qr code when offer is used and qr code feature is active', () => {
    // given
    props.isQrCodeFeatureDisabled = false
    props.booking.qrCode = null

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingTokenLink = wrapper.find('.mb-token-container').find(Link)
    expect(bookingTokenLink).toHaveLength(0)
  })

  it('should not render a link to booking qr code when offer is not used and qr code feature is inactive', () => {
    // given
    props.isQrCodeFeatureDisabled = true
    props.booking.qrCode = 'data:image/png;base64,iVIVhzdjeizfjezfoizejojczez'

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingTokenLink = wrapper.find('.mb-token-container').find(Link)
    expect(bookingTokenLink).toHaveLength(0)
  })

  it('should not render a link to booking qr code when offer is used and qr code feature is inactive', () => {
    // given
    props.isQrCodeFeatureDisabled = true
    props.booking.qrCode = null

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const bookingTokenLink = wrapper.find('.mb-token-container').find(Link)
    expect(bookingTokenLink).toHaveLength(0)
  })

  it('should render a token container when offer is not used, finished nor cancelled', () => {
    // given
    props.shouldDisplayToken = true

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const tokenContainer = wrapper.find('.mb-token-container')
    expect(tokenContainer).toHaveLength(1)
  })

  it('should not render a token container when offer is used, finished or cancelled', () => {
    // given
    props.shouldDisplayToken = false

    // when
    const wrapper = shallow(<BookingItem {...props} />)

    // then
    const tokenContainer = wrapper.find('.mb-token-container')
    expect(tokenContainer).toHaveLength(0)
  })
})
