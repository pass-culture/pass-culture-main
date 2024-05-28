import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React, { ComponentProps } from 'react'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared/types'
import * as filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import {
  collectiveBookingByIdFactory,
  collectiveBookingFactory,
} from 'utils/collectiveApiFactories'
import { bookingRecapFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BookingsRecapTable } from '../BookingsRecapTable'
import {
  EMPTY_FILTER_VALUE,
  DEFAULT_OMNISEARCH_CRITERIA,
} from '../Filters/constants'

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))
Element.prototype.scrollIntoView = vi.fn()

const bookingBeneficiaryCustom = {
  beneficiary: {
    lastname: 'Parjeot',
    firstname: 'Micheline',
    email: 'michelinedu72@example.com',
  },
}

const bookingInstitutionCustom = {
  institution: {
    id: 1,
    institutionType: 'COLLEGE',
    name: 'BELLEVUE',
    postalCode: '30100',
    city: 'Ales',
    phoneNumber: '',
    institutionId: 'ABCDEF11',
  },
}

describe('components | BookingsRecapTable', () => {
  type Props = ComponentProps<typeof BookingsRecapTable>

  const defaultProps: Props = {
    isLoading: false,
    audience: Audience.INDIVIDUAL,
    resetBookings: vi.fn(),
    bookingsRecap: [],
  }

  const renderBookingRecap = (props: Props, bookingId?: string) =>
    renderWithProviders(<BookingsRecapTable {...props} />, {
      initialRouterEntries: [
        `/reservations/collectives${
          bookingId ? `?bookingId=${bookingId}` : ''
        }`,
      ],
    })

  it('should filter when filters change', async () => {
    const bookingsRecap = [
      bookingRecapFactory(bookingBeneficiaryCustom),
      bookingRecapFactory(),
    ]
    const props: Props = {
      ...defaultProps,
      bookingsRecap: bookingsRecap,
    }
    renderBookingRecap(props)

    // 2 lines = 12 cells
    expect(screen.getAllByRole('cell')).toHaveLength(12)

    await userEvent.type(screen.getByRole('textbox'), 'Le nom de l’offre 2')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })

    await userEvent.selectOptions(
      screen.getByRole('combobox'),
      screen.getByRole('option', { name: 'Bénéficiaire' })
    )
    await userEvent.clear(screen.getByRole('textbox'))

    await waitFor(() => {
      // 2 lines = 12 cells
      expect(screen.getAllByRole('cell')).toHaveLength(12)
    })
    await userEvent.type(screen.getByRole('textbox'), 'Parjeot')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })
  })

  it('should filter bookings on render', () => {
    // Given
    const props: Props = {
      ...defaultProps,
      bookingsRecap: [bookingRecapFactory()],
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
    }
    vi.spyOn(filterBookingsRecap, 'filterBookingsRecap').mockReturnValue([])

    // When
    renderBookingRecap(props)

    // Then
    expect(filterBookingsRecap.filterBookingsRecap).toHaveBeenCalledWith(
      props.bookingsRecap,
      expect.objectContaining({
        bookingStatus: props.locationState?.statuses,
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
        selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      })
    )
  })

  it('should filter bookings collective on render', () => {
    vi.spyOn(api, 'getCollectiveBookingById').mockResolvedValue(
      collectiveBookingByIdFactory()
    )

    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: [collectiveBookingFactory({ bookingId: '123' })],
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
    }
    vi.spyOn(filterBookingsRecap, 'filterBookingsRecap').mockReturnValue([])

    // When
    renderBookingRecap(props, '123')

    // Then
    expect(filterBookingsRecap.filterBookingsRecap).toHaveBeenCalledWith(
      props.bookingsRecap,
      expect.objectContaining({
        bookingStatus: props.locationState?.statuses,
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
        selectedOmniSearchCriteria: 'booking_id',
      })
    )
  })

  it('should render the expected table with max given number of hits per page', () => {
    // Given
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue(bookingsRecap)
    const props: Props = {
      ...defaultProps,
      bookingsRecap: bookingsRecap,
    }

    // When
    renderBookingRecap(props)

    // Then
    // 1 line = 6 cells
    const cells = screen.getAllByRole('columnheader')
    expect(cells).toHaveLength(6)
    expect(cells[0]).toHaveTextContent('Nom de l’offre')
    expect(cells[1]).toHaveTextContent('')
    expect(cells[2]).toHaveTextContent('Bénéficiaire')
    expect(cells[3]).toHaveTextContent('Réservation')
    expect(cells[4]).toHaveTextContent('Contremarque')
    expect(cells[5]).toHaveTextContent('Statut')
  })

  it('should render the expected table for collective audience', () => {
    // Given
    const bookingRecap = collectiveBookingFactory(bookingInstitutionCustom)
    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue([bookingRecap])
    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: [bookingRecap],
    }

    // When
    renderBookingRecap(props)

    // Then
    // 1 line = 6 cells
    const cells = screen.getAllByRole('columnheader')
    expect(cells).toHaveLength(6)
    expect(cells[0]).toHaveTextContent('Réservation')
    expect(cells[1]).toHaveTextContent('Nom de l’offre')
    expect(cells[2]).toHaveTextContent('Établissement')
    expect(cells[3]).toHaveTextContent('Places et prix')
    expect(cells[4]).toHaveTextContent('Statut')
    expect(cells[5]).toHaveTextContent('Détails')
  })

  it('should not render a Header component when there is no filtered booking', () => {
    // given
    const props: Props = {
      ...defaultProps,
      bookingsRecap: [],
    }

    // When
    renderBookingRecap(props)

    // Then
    expect(
      screen.getByText('Aucune réservation trouvée pour votre recherche')
    ).toBeInTheDocument()
  })

  it('should reset filters when clicking on "Afficher toutes les réservations"', async () => {
    const props: Props = {
      ...defaultProps,
      bookingsRecap: [bookingRecapFactory()],
    }

    renderBookingRecap(props)

    await userEvent.type(screen.getByRole('textbox'), 'Le nom de l’offre 2')

    const displayAllBookingsButton = screen.getByRole('button', {
      name: /Afficher toutes les réservations/i,
    })

    await userEvent.click(displayAllBookingsButton)

    const offerName = screen.getByRole('textbox')
    expect(offerName).toHaveValue('')
  })

  it('should not show pagination when applying filters with no result', async () => {
    // given
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const props: Props = { ...defaultProps, bookingsRecap: bookingsRecap }
    renderBookingRecap(props)

    await userEvent.click(screen.getAllByRole('button')[1])

    // when
    await userEvent.type(screen.getByRole('textbox'), 'not findable')

    // then
    expect(screen.queryByText('Page 1/1')).not.toBeInTheDocument()
  })

  it('should log event when cliking collective row', async () => {
    // Given
    const bookingsRecap = [
      collectiveBookingFactory({ bookingId: 'mon booking id' }),
    ]
    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue(bookingsRecap)
    vi.spyOn(api, 'getCollectiveBookingById').mockResolvedValue(
      collectiveBookingByIdFactory()
    )

    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...vi.importActual('app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))

    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: bookingsRecap,
    }

    // When
    renderBookingRecap(props)
    await userEvent.click(screen.getAllByRole('button')[1])

    // Then
    const bookingRow = screen.getAllByRole('cell')
    expect(bookingRow[0]).toHaveTextContent('mon booking id')
    await userEvent.click(bookingRow[0])

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      CollectiveBookingsEvents.CLICKED_EXPAND_COLLECTIVE_BOOKING_DETAILS
    )
  })

  it('should update currentPage when clicking on next page button', async () => {
    const bookingsRecap = []
    for (let i = 0; i < 40; i++) {
      bookingsRecap.push(collectiveBookingFactory())
    }

    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: bookingsRecap,
    }

    // When
    renderBookingRecap(props)

    const nextPageButton = screen.getByRole('button', { name: 'Page suivante' })

    expect(screen.getByText('Page 1/2'))

    await userEvent.click(nextPageButton)

    expect(screen.getByText('Page 2/2'))
  })
})
