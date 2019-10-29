import React from 'react'
import { shallow } from 'enzyme'
import QrCode from '../QrCode'
import AbsoluteFooterContainer from '../../../../../../layout/AbsoluteFooter/AbsoluteFooterContainer'

describe('src | components | pages | my-bookings | MyBookingsList | BookingList | QrCode', () => {
  let props
  beforeEach(() => {
    props = {
      humanizedBeginningDatetime: 'Mercredi 06/11/2019 à 21:00',
      offerName: 'Un lit sous une rivière',
      qrCode: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIYAAACGAQAAAAAwAs88AAAD',
      token: 'ABCDE',
      venueName: 'Michel et son accordéon',
    }
  })

  it('should render booking informations when component is mounted', () => {
    // when
    const wrapper = shallow(<QrCode {...props} />)

    // then
    const offerName = wrapper.find('.qr-code-offer-name')
    const offerBeginningDatetime = wrapper.find('.qr-code-offer-beginning-datetime')
    const offerVenue = wrapper.find('.qr-code-venue-name')
    const bookingToken = wrapper.find('.qr-code-token')
    const bookingQrCode = wrapper.find('.qr-code-image').find('img')
    expect(offerName.text()).toBe('Un lit sous une rivière')
    expect(offerBeginningDatetime.text()).toBe('Mercredi 06/11/2019 à 21:00')
    expect(offerVenue.text()).toBe('Michel et son accordéon')
    expect(bookingToken.text()).toBe('abcde')
    expect(bookingQrCode.prop('alt')).toBe('')
    expect(bookingQrCode.prop('src')).toBe(
      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIYAAACGAQAAAAAwAs88AAAD'
    )
  })

  it('should render AbsoluteFooterContainer when component is mounted', () => {
    // when
    const wrapper = shallow(<QrCode {...props} />)

    // then
    const absoluteFooterContainer = wrapper.find(AbsoluteFooterContainer)
    expect(absoluteFooterContainer.prop('areDetailsVisible')).toBe(false)
    expect(absoluteFooterContainer.prop('borderTop')).toBe(true)
    expect(absoluteFooterContainer.prop('colored')).toBe(true)
    expect(absoluteFooterContainer.prop('id')).toBe('verso-footer')
  })
})
