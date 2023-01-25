import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'
import { configureTestStore } from 'store/testUtils'
import { bookingRecapFactory } from 'utils/apiFactories'

import FilterByBookingStatus from '../FilterByBookingStatus'
import { FilterByBookingStatusProps } from '../FilterByBookingStatus/FilterByBookingStatus'

const renderFilterByBookingStatus = (
  props: FilterByBookingStatusProps<
    BookingRecapResponseModel | CollectiveBookingResponseModel
  >
) => {
  const store = configureTestStore()
  return render(
    <MemoryRouter>
      <Provider store={store}>
        <FilterByBookingStatus {...props} />
      </Provider>
    </MemoryRouter>
  )
}

describe('components | FilterByBookingStatus', () => {
  let props: FilterByBookingStatusProps<
    BookingRecapResponseModel | CollectiveBookingResponseModel
  >
  beforeEach(() => {
    props = {
      bookingsRecap: [
        bookingRecapFactory({
          stock: {
            offerName: 'Avez-vous déjà vu',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          bookingDate: '2020-04-03T12:00:00Z',
          bookingToken: 'ZEHBGD',
          bookingStatus: 'booked',
          bookingIsDuo: false,
          venueIdentifier: 'AE',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-04-03T12:00:00Z',
            },
          ],
        }),
        bookingRecapFactory({
          stock: {
            offerName: 'Avez-vous déjà vu',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          bookingDate: '2020-04-03T12:00:00Z',
          bookingToken: 'ZEHBGD',
          bookingStatus: 'validated',
          bookingIsDuo: true,
          venueIdentifier: 'AF',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-04-03T12:00:00Z',
            },
          ],
        }),
      ],
      audience: Audience.INDIVIDUAL,
      bookingStatuses: [],
      updateGlobalFilters: jest.fn(),
    }
  })

  it('should display a black filter icon', () => {
    // when
    renderFilterByBookingStatus(props)

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
    renderFilterByBookingStatus(props)

    // then
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
  })

  describe('on focus on the filter icon', () => {
    it('should display a red filter icon', () => {
      // given
      renderFilterByBookingStatus(props)

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
      renderFilterByBookingStatus(props)
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
      renderFilterByBookingStatus(props)
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
      props.bookingStatuses = ['validated']
      renderFilterByBookingStatus(props)
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
      renderFilterByBookingStatus(props)
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
