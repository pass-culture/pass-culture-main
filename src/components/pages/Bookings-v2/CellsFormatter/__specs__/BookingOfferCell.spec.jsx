import { shallow } from 'enzyme/build'
import React from 'react'
import BookingOfferCell from '../BookingOfferCell'

describe('components | pages | bookings-v2 | CellsFormatter | BookingOfferCell', () => {
  it('should render a div with the props as content', () => {
    // Given
    const props = {
      offer: {
        offer_name: 'La danse des poireaux',
      },
    }

    // When
    const wrapper = shallow(<BookingOfferCell {...props} />)

    // Then
    const offerName = wrapper.find({ children: props.offer.offer_name })
    expect(offerName).toHaveLength(1)
  })
})
