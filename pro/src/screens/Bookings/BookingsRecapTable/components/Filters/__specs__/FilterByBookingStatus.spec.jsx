import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import FilterByBookingStatus from '../FilterByBookingStatus'

describe('components | FilterByBookingStatus', () => {
  let props
  beforeEach(() => {
    props = {
      bookingsRecap: [
        {
          stock: {
            offer_name: 'Avez-vous déjà vu',
            type: 'thing',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
          booking_status: 'booked',
          booking_is_duo: false,
          venue_identifier: 'AE',
          booking_status_history: [
            {
              status: 'booked',
              date: '2020-04-03T12:00:00Z',
            },
          ],
        },
        {
          stock: {
            offer_name: 'Avez-vous déjà vu',
            type: 'thing',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
          booking_status: 'validated',
          booking_is_duo: true,
          venue_identifier: 'AF',
          booking_status_history: [
            {
              status: 'booked',
              date: '2020-04-03T12:00:00Z',
            },
          ],
        },
      ],
      bookingStatuses: [],
      updateGlobalFilters: jest.fn(),
    }
  })

  it('should display a black filter icon', () => {
    // when
    render(<FilterByBookingStatus {...props} />)

    // then
    const filterIcon = screen.getByRole('img')
    expect(filterIcon).toHaveAttribute(
      'src',
      expect.stringContaining('ico-filter-status-black.svg')
    )
    expect(filterIcon).toHaveAttribute('alt', 'Filtrer par statut')
  })

  it('should not display status filters', () => {
    // when
    render(<FilterByBookingStatus {...props} />)

    // then
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
  })

  describe('on focus on the filter icon', () => {
    it('should display a red filter icon', () => {
      // given
      render(<FilterByBookingStatus {...props} />)

      // when
      screen.getByRole('button').focus()

      // then
      const filterIcon = screen.getByRole('img')
      expect(filterIcon).toHaveAttribute(
        'src',
        expect.stringContaining('ico-filter-status-red.svg')
      )
      expect(filterIcon).toHaveAttribute('alt', 'Filtrer par statut')
    })

    it('should show filters with all available status in data', async () => {
      // given
      render(<FilterByBookingStatus {...props} />)
      await userEvent.click(screen.getByRole('img'))

      // then
      const checkbox = screen.getAllByRole('checkbox')
      expect(checkbox).toHaveLength(2)
      expect(checkbox[0]).toHaveAttribute('checked')
      expect(checkbox[1]).toHaveAttribute('checked')
      expect(screen.getByText('réservé')).toBeInTheDocument()
      expect(screen.getByText('validé')).toBeInTheDocument()
    })

    it('should add value to filters when unchecking on a checkbox', async () => {
      // given
      render(<FilterByBookingStatus {...props} />)
      await userEvent.click(screen.getByRole('img'))
      const checkbox = screen.getAllByRole('checkbox')[1]

      // when
      checkbox.click()
      // then
      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated'],
      })
    })

    it('should remove value from filters when checking the checkbox', async () => {
      // given
      const propsWithInitialFilter = {
        ...props,
        bookingStatuses: ['validated'],
      }
      render(<FilterByBookingStatus {...propsWithInitialFilter} />)
      await userEvent.click(screen.getByRole('img'))

      const checkbox = screen.getAllByRole('checkbox')[1]

      // when
      checkbox.click()

      // then
      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: [],
      })
    })

    it('should add value to already filtered booking status when clicking on a checkbox', async () => {
      // given
      render(<FilterByBookingStatus {...props} />)
      await userEvent.click(screen.getByRole('img'))

      const validatedStatusCheckbox = screen.getAllByRole('checkbox')[1]
      validatedStatusCheckbox.click()
      const bookedStatusCheckbox = screen.getAllByRole('checkbox')[0]

      // when
      bookedStatusCheckbox.click()

      // then
      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated', 'booked'],
      })
    })
  })
})
