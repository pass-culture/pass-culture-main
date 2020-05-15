import { mount } from 'enzyme/build'
import React from 'react'
import BookingOfferCell from '../BookingOfferCell'

describe('components | pages | bookings-v2 | CellsFormatter | BookingOfferCell', () => {
  describe('render a thing stock', () => {
    it('should render offer name', () => {
      // Given
      const props = {
        offer: {
          type: 'thing',
          offer_name: 'Guitare acoustique',
        },
      }

      // When
      const wrapper = mount(<BookingOfferCell {...props} />)

      // Then
      const offerName = wrapper.find({ children: props.offer.offer_name })
      expect(offerName).toHaveLength(1)
    })
  })

  describe('render an event stock', () => {
    it('should render offer name and event beginning datetime in venue timezone', () => {
      // Given
      const props = {
        offer: {
          type: 'event',
          offer_name: 'La danse des poireaux',
          event_beginning_datetime: '2020-05-12T12:03:28.564687Z',
          venue_department_code: '973',
        },
      }

      // When
      const wrapper = mount(<BookingOfferCell {...props} />)

      // Then
      const offerName = wrapper.find({ children: props.offer.offer_name })
      expect(offerName).toHaveLength(1)

      const eventDatetime = wrapper.find("[children^='12/05/2020']")
      expect(eventDatetime).toHaveLength(1)
      expect(eventDatetime.text()).toContain('9:03')
    })
  })
})
