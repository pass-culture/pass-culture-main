import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { ComponentProps } from 'react'

import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from 'screens/Bookings/BookingsRecapTable/components/Filters/_constants'
import * as bookingDetailsAdapter from 'screens/Bookings/BookingsRecapTable/components/Table/Body/TableRow/adapters/getCollectiveBookingAdapter'
import * as filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import { bookingRecapFactory } from 'utils/apiFactories'
import {
  collectiveBookingDetailsFactory,
  collectiveBookingRecapFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import BookingsRecapTable from '../BookingsRecapTable'

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
    reloadBookings: vi.fn(),
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
    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue([])

    // When
    renderBookingRecap(props)

    // Then
    expect(filterBookingsRecap.default).toHaveBeenCalledWith(
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

  it('should filter bookings collective on render', async () => {
    vi.spyOn(bookingDetailsAdapter, 'default').mockResolvedValue({
      isOk: true,
      message: '',
      payload: collectiveBookingDetailsFactory(),
    })
    // Given
    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: [collectiveBookingRecapFactory({ bookingId: '123' })],
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
    }
    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue([])

    // When
    renderBookingRecap(props, '123')

    // Then
    expect(filterBookingsRecap.default).toHaveBeenCalledWith(
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
    const bookingRecap = bookingRecapFactory(bookingInstitutionCustom)
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
    expect(cells[5]).toHaveTextContent('')
  })

  it('should not render a Header component when there is no filtered booking', async () => {
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

  it('should reset filters when clicking on "afficher toutes les réservations"', async () => {
    // given
    const props: Props = {
      ...defaultProps,
      bookingsRecap: [bookingRecapFactory()],
    }

    renderBookingRecap(props)

    await userEvent.type(screen.getByRole('textbox'), 'Le nom de l’offre 2')

    const displayAllBookingsButton = screen.getByRole('button', {
      name: /afficher toutes les réservations/i,
    })

    // When
    await userEvent.click(displayAllBookingsButton)

    // Then
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
      collectiveBookingRecapFactory({ bookingId: 'mon booking id' }),
    ]
    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue(bookingsRecap)
    vi.spyOn(bookingDetailsAdapter, 'default').mockResolvedValue({
      isOk: true,
      message: '',
      payload: collectiveBookingDetailsFactory(),
    })

    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...vi.importActual('hooks/useAnalytics'),
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

  it('should not re-open reservation when there is bookingId in the url but bookingId filter changed', async () => {
    const bookingsRecap = [collectiveBookingRecapFactory({ bookingId: '123' })]

    vi.spyOn(filterBookingsRecap, 'default').mockReturnValue([])

    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: bookingsRecap,
    }

    // When
    renderBookingRecap(props, '123')

    const omniSearchOption = screen.getByRole('combobox')

    await userEvent.selectOptions(omniSearchOption, 'booking_id')

    const bookingIdOmnisearchFilter = await screen.getByPlaceholderText(
      'Rechercher par numéro de réservation'
    )

    await userEvent.clear(bookingIdOmnisearchFilter)

    expect(
      screen.queryByText('Contact de l’établissement scolaire')
    ).not.toBeInTheDocument()
  })

  it('should update currentPage when clicking on next page button', async () => {
    const bookingsRecap = []
    for (let i = 0; i < 40; i++) {
      bookingsRecap.push(collectiveBookingRecapFactory())
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
