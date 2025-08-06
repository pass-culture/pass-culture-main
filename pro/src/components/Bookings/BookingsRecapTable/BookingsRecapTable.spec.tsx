import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { ComponentProps } from 'react'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import { Audience } from '@/commons/core/shared/types'
import {
  collectiveBookingByIdFactory,
  collectiveBookingCollectiveStockFactory,
  collectiveBookingFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { bookingRecapFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import * as filterBookingsRecap from '@/components/Bookings/BookingsRecapTable/utils/filterBookingsRecap'

import { BookingsRecapTable } from './BookingsRecapTable'
import {
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Filters/constants'

vi.mock('@/commons/utils/windowMatchMedia', () => ({
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

    await userEvent.type(screen.getByRole('searchbox'), 'Le nom de l’offre 2')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })

    await userEvent.selectOptions(
      screen.getByRole('combobox'),
      screen.getByRole('option', { name: 'Bénéficiaire' })
    )
    await userEvent.clear(screen.getByRole('searchbox'))

    await waitFor(() => {
      // 2 lines = 12 cells
      expect(screen.getAllByRole('cell')).toHaveLength(12)
    })
    await userEvent.type(screen.getByRole('searchbox'), 'Parjeot')
    await waitFor(() => {
      // 1 line = 5
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

  it('should sort by offer name', async () => {
    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: [
        collectiveBookingFactory({
          bookingId: '123',
          stock: collectiveBookingCollectiveStockFactory({
            offerName: 'Offre de test 2',
          }),
        }),
        collectiveBookingFactory({
          bookingId: '456',
          stock: collectiveBookingCollectiveStockFactory({
            offerName: 'Offre de test 1',
          }),
        }),
        collectiveBookingFactory({
          bookingId: '789',
          stock: collectiveBookingCollectiveStockFactory({
            offerName: 'Offre de test 3',
          }),
        }),
      ],
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
    }

    const filter = vi.spyOn(filterBookingsRecap, 'filterBookingsRecap')
    renderBookingRecap(props)

    expect(filter).toHaveBeenCalledOnce()

    await userEvent.click(
      within(screen.getByText('Nom de l’offre').closest('th')!).getByRole(
        'button'
      )
    )

    expect(filter).toHaveBeenCalledOnce()

    expect(screen.getAllByTestId('booking-offer-name')[0]).toHaveTextContent(
      /Offre de test 1/
    )
    expect(screen.getAllByTestId('booking-offer-name')[1]).toHaveTextContent(
      /Offre de test 2/
    )
    expect(screen.getAllByTestId('booking-offer-name')[2]).toHaveTextContent(
      /Offre de test 3/
    )

    await userEvent.click(
      within(screen.getByText('Nom de l’offre').closest('th')!).getByRole(
        'button'
      )
    )
    expect(filter).toHaveBeenCalledOnce()

    expect(screen.getAllByTestId('booking-offer-name')[0]).toHaveTextContent(
      /Offre de test 3/
    )
    expect(screen.getAllByTestId('booking-offer-name')[1]).toHaveTextContent(
      /Offre de test 2/
    )
    expect(screen.getAllByTestId('booking-offer-name')[2]).toHaveTextContent(
      /Offre de test 1/
    )
  })

  it('should sort by institution name', async () => {
    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: [
        collectiveBookingFactory({
          bookingId: '123',
          institution: {
            id: 1,
            name: 'Collège 2',
            city: 'City',
            postalCode: '11111',
            institutionId: 'ABCDEF',
            institutionType: 'COLLEGE',
            phoneNumber: '0102030405',
          },
          stock: collectiveBookingCollectiveStockFactory({
            offerName: 'Offre de test 2',
          }),
        }),
        collectiveBookingFactory({
          bookingId: '456',
          institution: {
            id: 2,
            name: 'Collège 1',
            city: 'City',
            postalCode: '11111',
            institutionId: 'ABCDEF',
            institutionType: 'COLLEGE',
            phoneNumber: '0102030405',
          },
          stock: collectiveBookingCollectiveStockFactory({
            offerName: 'Offre de test 1',
          }),
        }),
        collectiveBookingFactory({
          bookingId: '789',
          institution: {
            id: 3,
            name: 'Collège 3',
            city: 'City',
            postalCode: '11111',
            institutionId: 'ABCDEF',
            institutionType: 'COLLEGE',
            phoneNumber: '0102030405',
          },
          stock: collectiveBookingCollectiveStockFactory({
            offerName: 'Offre de test 3',
          }),
        }),
      ],
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
    }

    const filter = vi.spyOn(filterBookingsRecap, 'filterBookingsRecap')
    renderBookingRecap(props)
    expect(filter).toHaveBeenCalledOnce()

    await userEvent.click(
      within(screen.getByTestId('institution-column')).getByRole('button')
    )
    expect(filter).toHaveBeenCalledOnce()

    expect(
      screen.getAllByTestId('booking-offer-institution')[0]
    ).toHaveTextContent(/Collège 1/)

    expect(
      screen.getAllByTestId('booking-offer-institution')[1]
    ).toHaveTextContent(/Collège 2/)
    expect(
      screen.getAllByTestId('booking-offer-institution')[2]
    ).toHaveTextContent(/Collège 3/)

    await userEvent.click(
      within(screen.getByTestId('institution-column')).getByRole('button')
    )
    expect(filter).toHaveBeenCalledOnce()

    expect(
      screen.getAllByTestId('booking-offer-institution')[0]
    ).toHaveTextContent(/Collège 3/)
    expect(
      screen.getAllByTestId('booking-offer-institution')[1]
    ).toHaveTextContent(/Collège 2/)
    expect(
      screen.getAllByTestId('booking-offer-institution')[2]
    ).toHaveTextContent(/Collège 1/)
  })

  it('should render the expected table with max given number of hits per page', () => {
    // Given
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    vi.spyOn(filterBookingsRecap, 'filterBookingsRecap').mockReturnValue(
      bookingsRecap
    )
    const props: Props = {
      ...defaultProps,
      bookingsRecap: bookingsRecap,
    }

    // When
    renderBookingRecap(props)

    // Then
    // 1 line = 5 cells
    const cells = screen.getAllByRole('columnheader')
    expect(cells).toHaveLength(5)
    expect(cells[0]).toHaveTextContent('Nom de l’offre')
    expect(cells[1]).toHaveTextContent('Bénéficiaire')
    expect(cells[2]).toHaveTextContent('Réservation')
    expect(cells[3]).toHaveTextContent('Contremarque')
    expect(cells[4]).toHaveTextContent('Statut')
  })

  it('should render the expected table for collective audience', () => {
    // Given
    const bookingRecap = collectiveBookingFactory(bookingInstitutionCustom)
    vi.spyOn(filterBookingsRecap, 'filterBookingsRecap').mockReturnValue([
      bookingRecap,
    ])
    const props: Props = {
      ...defaultProps,
      audience: Audience.COLLECTIVE,
      bookingsRecap: [bookingRecap],
    }

    // When
    renderBookingRecap(props)

    // Then
    // 1 line = 6
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

    await userEvent.type(screen.getByRole('searchbox'), 'Le nom de l’offre 2')

    const displayAllBookingsButton = screen.getByRole('button', {
      name: /Afficher toutes les réservations/i,
    })

    await userEvent.click(displayAllBookingsButton)

    const offerName = screen.getByRole('searchbox')
    expect(offerName).toHaveValue('')
  })

  it('should not show pagination when applying filters with no result', async () => {
    // given
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    const props: Props = { ...defaultProps, bookingsRecap: bookingsRecap }
    renderBookingRecap(props)

    await userEvent.click(screen.getAllByRole('button')[1])

    // when
    await userEvent.type(screen.getByRole('searchbox'), 'not findable')

    // then
    expect(screen.queryByText('Page 1/1')).not.toBeInTheDocument()
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
