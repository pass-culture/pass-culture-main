import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  BookingRecapResponseModel,
  BookingRecapStatus,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { Audience } from '@/commons/core/shared/types'
import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  FilterByBookingStatus,
  FilterByBookingStatusProps,
} from '../FilterByBookingStatus'

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
          stock: bookingRecapStockFactory({
            offerName: 'Avez-vous déjà vu',
          }),
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          bookingDate: '2020-04-03T12:00:00Z',
          bookingToken: 'ZEHBGD',
          bookingStatus: BookingRecapStatus.BOOKED,
          bookingIsDuo: false,
          bookingStatusHistory: [
            {
              status: BookingRecapStatus.BOOKED,
              date: '2020-04-03T12:00:00Z',
            },
          ],
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({
            offerName: 'Avez-vous déjà vu',
          }),
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          bookingDate: '2020-04-03T12:00:00Z',
          bookingToken: 'ZEHBGD',
          bookingStatus: BookingRecapStatus.VALIDATED,
          bookingIsDuo: true,
          bookingStatusHistory: [
            {
              status: BookingRecapStatus.BOOKED,
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

    it('should close the tooltip when the Escape key is pressed', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('img'))

      expect(screen.getByText('Afficher les réservations')).toBeInTheDocument()

      await userEvent.keyboard('{Escape}')

      expect(
        screen.queryByText('Afficher les réservations')
      ).not.toBeInTheDocument()
    })

    it('should toggle the opening of the tooltip panel when the Space key is pressd', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('img'))

      await userEvent.keyboard('{Space}')

      expect(
        screen.queryByText('Afficher les réservations')
      ).not.toBeInTheDocument()

      await userEvent.keyboard('{Space}')

      expect(screen.getByText('Afficher les réservations')).toBeInTheDocument()
    })
  })
})
