import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  FilterByBookingStatus,
  type FilterByBookingStatusProps,
} from '../FilterByBookingStatus'

const renderFilterByBookingStatus = (props: FilterByBookingStatusProps) =>
  renderWithProviders(<FilterByBookingStatus {...props} />)

describe('components | FilterByBookingStatus', () => {
  let props: FilterByBookingStatusProps
  beforeEach(() => {
    props = {
      bookingStatuses: [],
      updateGlobalFilters: vi.fn(),
    }
  })

  it('should display a black filter icon', () => {
    const { container } = renderFilterByBookingStatus(props)

    const filterIcon = container.querySelector('svg')
    expect(filterIcon).not.toHaveAttribute(
      'class',
      expect.stringContaining('active')
    )
    expect(filterIcon).toHaveAttribute('aria-hidden', 'true')
  })

  it('should announce that all booking statuses are displayed', () => {
    renderFilterByBookingStatus(props)

    expect(
      screen.getByRole('button', { name: 'Statut' })
    ).toHaveAccessibleDescription('Tous les statuts sont affichés')
  })

  it('should not display status filters', () => {
    renderFilterByBookingStatus(props)

    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
  })

  describe('when using the filter button', () => {
    it('should display a red filter icon', async () => {
      const { container } = renderFilterByBookingStatus(props)

      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      const filterIcon = container.querySelector('svg')
      expect(filterIcon).toHaveAttribute(
        'class',
        expect.stringContaining('active')
      )
      expect(filterIcon).toHaveAttribute('aria-hidden', 'true')
    })

    it('should expose the filter panel opening state to assistive technologies', async () => {
      renderFilterByBookingStatus(props)

      const filterButton = screen.getByRole('button', { name: 'Statut' })
      expect(filterButton).toHaveAttribute('aria-expanded', 'false')

      await userEvent.click(filterButton)

      const filterPanel = screen
        .getByText('Afficher les réservations')
        .closest('[id]')
      expect(filterButton).toHaveAttribute('aria-expanded', 'true')
      expect(filterButton).toHaveAttribute(
        'aria-controls',
        filterPanel?.getAttribute('id')
      )
    })

    it('should show filters with all available statuses', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      const checkbox = screen.getAllByRole('checkbox')
      expect(checkbox).toHaveLength(5)
      expect(checkbox[0]).toHaveAttribute('checked')
      expect(checkbox[1]).toHaveAttribute('checked')
      expect(screen.getByText('Réservée')).toBeInTheDocument()
      expect(screen.getByText('Validée')).toBeInTheDocument()
    })

    it('should add value to filters when unchecking on a checkbox', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      await userEvent.click(screen.getByLabelText('Validée'))

      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated'],
      })
    })

    it('should remove value from filters when checking the checkbox', async () => {
      props.bookingStatuses = ['validated']
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      await userEvent.click(screen.getByLabelText('Validée'))

      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: [],
      })
    })

    it('should add value to already filtered booking status when clicking on a checkbox', async () => {
      props.bookingStatuses = ['validated']
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      const bookedStatusCheckbox = screen.getByLabelText('Réservée')
      await userEvent.click(bookedStatusCheckbox)

      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated', 'booked'],
      })
    })

    it('should communicate the selected status filter values', async () => {
      props.bookingStatuses = ['validated']
      renderFilterByBookingStatus(props)

      expect(
        screen.getByRole('button', { name: 'Statut' })
      ).toHaveAccessibleDescription('1 statut masqué : Validée')

      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      expect(screen.getByRole('checkbox', { name: 'Réservée' })).toBeChecked()
      expect(
        screen.getByRole('checkbox', { name: 'Validée' })
      ).not.toBeChecked()
    })

    it('should close the tooltip when the Escape key is pressed', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      expect(screen.getByText('Afficher les réservations')).toBeInTheDocument()

      await userEvent.keyboard('{Escape}')

      expect(
        screen.queryByText('Afficher les réservations')
      ).not.toBeInTheDocument()
    })

    it('should toggle the opening of the tooltip panel when the Space key is pressed', async () => {
      renderFilterByBookingStatus(props)
      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      await userEvent.keyboard('{Space}')

      expect(
        screen.queryByText('Afficher les réservations')
      ).not.toBeInTheDocument()

      await userEvent.keyboard('{Space}')

      expect(screen.getByText('Afficher les réservations')).toBeInTheDocument()
    })
  })
})
