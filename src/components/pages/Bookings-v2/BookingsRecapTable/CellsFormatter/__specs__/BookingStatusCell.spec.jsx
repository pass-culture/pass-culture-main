import { shallow, mount } from 'enzyme/build'
import React from 'react'
import BookingStatusCell from '../BookingStatusCell'
import BookingStatusCellHistory from "../BookingStatusCellHistory"

describe('components | pages | bookings-v2 | CellsFormatter | BookingsStatusCell', () => {
  it('should render a div with the corresponding tag value and tag classnames for the given status', () => {
    // Given
    const props = {
      bookingRecapInfo: {
        original: {
          stock: {
            event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
            offer_name: 'Matrix',
            type: 'event',
          },
          booking_is_duo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          booking_date: '2020-01-04T20:31:12+01:00',
          booking_token: '5U7M6U',
          booking_status: 'validated',
          booking_recap_history: {
            booking_date: '2020-01-04T20:31:12+01:00',
          }
        },
      },
    }

    // When
    const wrapper = shallow(<BookingStatusCell {...props} />)
    const status = wrapper.find({children: 'validé'})

    // Then
    expect(status.hasClass('booking-status-label')).toBe(true)
    expect(status.hasClass('booking-status-validated')).toBe(true)
  })

  it('should render a div with the default tag classname for an unknown status', () => {
    // Given
    const props = {
      bookingRecapInfo: {
        original: {
          stock: {
            event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
            offer_name: 'Matrix',
            type: 'event',
          },
          booking_is_duo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          booking_date: '2020-01-04T20:31:12+01:00',
          booking_token: '5U7M6U',
          booking_status: 'unknown',
          booking_recap_history: {
            booking_date: '2020-01-04T20:31:12+01:00',
          }
        },
      },
    }

    // When
    const wrapper = shallow(<BookingStatusCell {...props} />)
    const status = wrapper.find({children: 'unknown'})

    // Then
    expect(status.hasClass('booking-status-label')).toBe(true)
    expect(status.hasClass('booking-status-default')).toBe(true)
  })

  describe('Tooltip', () => {
    it('should always display the offer title and history title and amount when it is not free', () => {
      // Given
      const expectedHistoryTitle = "Historique"
      const props = {
        bookingRecapInfo: {
          original: {
            stock: {
              event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
              offer_name: 'Matrix',
              type: 'event',
            },
            booking_is_duo: true,
            beneficiary: {
              email: 'loulou.duck@example.com',
              firstname: 'Loulou',
              lastname: 'Duck',
            },
            booking_date: '2020-01-04T20:31:12+01:00',
            booking_token: '5U7M6U',
            booking_status: 'unknown',
            booking_amount: '10',
            booking_recap_history: {
              booking_date: '2020-01-04T20:31:12+01:00',
            }
          },
        },
      }

      // When
      const wrapper = shallow(<BookingStatusCell {...props} />)
      const offer = wrapper.find('.bs-offer-title')
      const historique = wrapper.find({children: expectedHistoryTitle})

      // Then
      expect(offer).toHaveLength(1)
      expect(offer.text()).toBe('Matrix')
      expect(historique).toHaveLength(1)
    })

    it('should display the booking amount when it is not free', () => {
      // Given
      const expectedAmount = "Prix: 10€"
      const props = {
        bookingRecapInfo: {
          original: {
            stock: {
              event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
              offer_name: 'Matrix',
              type: 'event',
            },
            booking_is_duo: true,
            beneficiary: {
              email: 'loulou.duck@example.com',
              firstname: 'Loulou',
              lastname: 'Duck',
            },
            booking_date: '2020-01-04T20:31:12+01:00',
            booking_token: '5U7M6U',
            booking_status: 'unknown',
            booking_amount: '10',
            booking_recap_history: {
              booking_date: '2020-01-04T20:31:12+01:00',
            }
          },
        },
      }

      // When
      const wrapper = shallow(<BookingStatusCell {...props} />)
      const amount = wrapper.find('.bs-offer-amount')

      // Then
      expect(amount.text()).toBe(expectedAmount)
    })

    it('should display Prix: Gratuit when the offer is free', () => {
      // Given
      const expectedAmount = "Prix: Gratuit"
      const props = {
        bookingRecapInfo: {
          original: {
            stock: {
              event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
              offer_name: 'Matrix',
              type: 'event',
            },
            booking_is_duo: true,
            beneficiary: {
              email: 'loulou.duck@example.com',
              firstname: 'Loulou',
              lastname: 'Duck',
            },
            booking_date: '2020-01-04T20:31:12+01:00',
            booking_token: '5U7M6U',
            booking_status: 'unknown',
            booking_recap_history: {
              booking_date: '2020-01-04T20:31:12+01:00',
            }
          },
        },
      }

      // When
      const wrapper = shallow(<BookingStatusCell {...props} />)
      const amount = wrapper.find('.bs-offer-amount')

      // Then
      expect(amount).toHaveLength(1)
      expect(amount.text()).toBe(expectedAmount)
    })

    it('should display as many BookingStatusCellHistory Component as dates present in booking recap history', () => {
      // Given
      const props = {
        bookingRecapInfo: {
          original: {
            stock: {
              event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
              offer_name: 'Matrix',
              type: 'event',
            },
            booking_is_duo: true,
            beneficiary: {
              email: 'loulou.duck@example.com',
              firstname: 'Loulou',
              lastname: 'Duck',
            },
            booking_date: '2020-01-04T20:31:12+01:00',
            booking_token: '5U7M6U',
            booking_status: 'unknown',
            booking_recap_history: {
              booking_date: '2020-01-04T20:31:12+01:00',
              date_used: '2020-03-04T20:31:12+01:00',
              reimbursed_date: '2020-03-04T20:44:12+01:00',
              cancellation_date: '2020-03-04T20:44:12+01:00',
            }
          },
        },
      }

      // When
      const wrapper = mount(<BookingStatusCell {...props} />)
      const historyCells = wrapper.find(BookingStatusCellHistory)
      const historyBookedCell = historyCells.at(0)
      const cancelledBookedCell = historyCells.at(1)
      const validatedBookedCell = historyCells.at(2)
      const reimbursedBookedCell = historyCells.at(3)

      // Then
      expect(historyCells).toHaveLength(4)
      expect(historyBookedCell.props()).toStrictEqual({
        "historyDate": "2020-01-04T20:31:12+01:00",
        "historyDateType": "booking_date"
      })
      expect(cancelledBookedCell.props()).toStrictEqual({
        "historyDate": "2020-03-04T20:44:12+01:00",
        "historyDateType": "cancellation_date"
      })
      expect(validatedBookedCell.props()).toStrictEqual({
        "historyDate": "2020-03-04T20:31:12+01:00",
        "historyDateType": "date_used"
      })
      expect(reimbursedBookedCell.props()).toStrictEqual({
        "historyDate": "2020-03-04T20:44:12+01:00",
        "historyDateType": "payment_date"
      })
    })
  })
})
