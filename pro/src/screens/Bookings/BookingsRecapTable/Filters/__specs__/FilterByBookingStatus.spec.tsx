import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'
import { bookingRecapFactory } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import FilterByBookingStatus from '../FilterByBookingStatus'
import { FilterByBookingStatusProps } from '../FilterByBookingStatus/FilterByBookingStatus'

const renderFilterByBookingStatus = (
  props: FilterByBookingStatusProps<
    BookingRecapResponseModel | CollectiveBookingResponseModel
  >
) => renderWithProviders(<FilterByBookingStatus {...props} />)

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
      updateGlobalFilters: vi.fn(),
    }
  })

  it('should display a black filter icon', () => {
    renderFilterByBookingStatus(props)

    const filterIcon = screen.getByRole('img')
    expect(filterIcon).not.toHaveAttribute(
      'class',
      expect.stringContaining('active')
    )
    expect(filterIcon).toHaveAttribute('aria-label', 'Filtrer par statut')
  })

  it('should not display status filters', () => {
    renderFilterByBookingStatus(props)

    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
  })

  describe('on focus on the filter icon', () => {
    it('should display a red filter icon', async () => {
      renderFilterByBookingStatus(props)

      await userEvent.click(screen.getByRole('button'))

      const filterIcon = screen.getByRole('img')
      expect(filterIcon).toHaveAttribute(
        'class',
        expect.stringContaining('active')
      )
      expect(filterIcon).toHaveAttribute('aria-label', 'Filtrer par statut')
    })

    it('should show filters with all available statuses', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('img'))

      const checkbox = screen.getAllByRole('checkbox')
      expect(checkbox).toHaveLength(5)
      expect(checkbox[0]).toHaveAttribute('checked')
      expect(checkbox[1]).toHaveAttribute('checked')
      expect(screen.getByText('Réservée')).toBeInTheDocument()
      expect(screen.getByText('Validée')).toBeInTheDocument()
    })

    it('should add value to filters when unchecking on a checkbox', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('img'))

      await userEvent.click(screen.getByLabelText('Validée'))

      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated'],
      })
    })

    it('should remove value from filters when checking the checkbox', async () => {
      props.bookingStatuses = ['validated']
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('img'))

      await userEvent.click(screen.getByLabelText('Validée'))

      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: [],
      })
    })

    it('should add value to already filtered booking status when clicking on a checkbox', async () => {
      props.bookingStatuses = ['validated']
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('img'))

      const bookedStatusCheckbox = screen.getByLabelText('Réservée')
      await userEvent.click(bookedStatusCheckbox)

      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated', 'booked'],
      })
    })
  })
})
