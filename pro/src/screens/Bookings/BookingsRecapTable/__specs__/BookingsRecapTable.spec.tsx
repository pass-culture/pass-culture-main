import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { ComponentProps } from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import type { Store } from 'redux'

import { Audience } from 'core/shared'
import { EMPTY_FILTER_VALUE } from 'screens/Bookings/BookingsRecapTable/components/Filters/_constants'
import * as constants from 'screens/Bookings/BookingsRecapTable/constants/NB_BOOKINGS_PER_PAGE'
import * as filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { bookingRecapFactory } from 'utils/apiFactories'

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
  let store: Store<Partial<RootState>>
  type Props = ComponentProps<typeof BookingsRecapTable>

  const renderBookingRecap = (props: Props) => {
    return render(
      <MemoryRouter initialEntries={['/reservations/collectives']}>
        <Provider store={store}>
          <BookingsRecapTable {...props} />
        </Provider>
      </MemoryRouter>
    )
  }

  beforeEach(() => {
    store = configureTestStore({})
  })

  it('should filter when filters change', async () => {
    const bookingsRecap = [
      bookingRecapFactory(bookingBeneficiaryCustom),
      bookingRecapFactory(),
    ]
    const props: Props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
      audience: Audience.INDIVIDUAL,
      reloadBookings: jest.fn(),
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
      bookingsRecap: [bookingRecapFactory()],
      isLoading: false,
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
      audience: Audience.INDIVIDUAL,
      reloadBookings: jest.fn(),
    }
    jest.spyOn(filterBookingsRecap, 'default').mockReturnValue([])

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
      })
    )
  })

  it('should render the expected table with max given number of hits per page', () => {
    // Given
    // @ts-ignore
    // eslint-disable-next-line
    constants.NB_BOOKINGS_PER_PAGE = 1
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    jest.spyOn(filterBookingsRecap, 'default').mockReturnValue(bookingsRecap)
    const props: Props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
      audience: Audience.INDIVIDUAL,
      reloadBookings: jest.fn(),
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
    // @ts-ignore
    // eslint-disable-next-line
    constants.NB_BOOKINGS_PER_PAGE = 1
    const bookingRecap = bookingRecapFactory(bookingInstitutionCustom)
    jest.spyOn(filterBookingsRecap, 'default').mockReturnValue([bookingRecap])
    const props: Props = {
      bookingsRecap: [bookingRecap],
      isLoading: false,
      audience: Audience.COLLECTIVE,
      reloadBookings: jest.fn(),
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
      bookingsRecap: [],
      audience: Audience.INDIVIDUAL,
      isLoading: false,
      reloadBookings: jest.fn(),
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
      audience: Audience.INDIVIDUAL,
      bookingsRecap: [bookingRecapFactory()],
      isLoading: false,
      reloadBookings: jest.fn(),
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
    const props: Props = {
      audience: Audience.INDIVIDUAL,
      bookingsRecap: bookingsRecap,
      isLoading: false,
      reloadBookings: jest.fn(),
    }
    renderBookingRecap(props)

    await userEvent.click(screen.getAllByRole('button')[1])

    // when
    await userEvent.type(screen.getByRole('textbox'), 'not findable')

    // then
    expect(screen.queryByText('Page 1/1')).not.toBeInTheDocument()
  })

  it('should update currentPage when clicking on next page button', async () => {
    // Given
    const spyOnFilterBookingsRecap = jest.spyOn(filterBookingsRecap, 'default')
    const bookingsRecap = [bookingRecapFactory(), bookingRecapFactory()]
    spyOnFilterBookingsRecap.mockReturnValue(bookingsRecap)

    const props: Props = {
      audience: Audience.INDIVIDUAL,
      bookingsRecap: bookingsRecap,
      isLoading: false,
      reloadBookings: jest.fn(),
    }

    // When
    renderBookingRecap(props)
    await userEvent.click(screen.getAllByRole('button')[1])

    // Then
    const bookingRow = screen.getAllByRole('cell')

    expect(spyOnFilterBookingsRecap).toHaveBeenCalled()
    expect(bookingRow[0]).toHaveTextContent('Le nom de l’offre')
  })
})
