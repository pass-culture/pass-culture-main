import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api, apiNew } from '@/apiClient/api'
import type { GetVenueAddressResponseModel } from '@/apiClient/v1/new'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { ALL_OFFERER_ADDRESS_OPTION } from '@/commons/core/Offers/constants'
import type { DeepPartial } from '@/commons/custom_types/utils'
import type { RootState } from '@/commons/store/store'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from '@/commons/utils/date'
import {
  bookingRecapFactory,
  defaultGetOffererVenueResponseModel,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  venueAddressFactory,
} from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import { PartnerLayout } from '@/layouts/PartnerLayout/PartnerLayout'

import { IndividualBookings } from './IndividualBookings'

const individualBookingsRoutes = [
  {
    path: '/',
    Component: PartnerLayout,
    children: [
      {
        path: 'reservations',
        element: (
          <>
            <IndividualBookings />
            <SnackBarContainer />
          </>
        ),
        handle: { title: 'Réservations individuelles' },
      },
    ],
  },
]

const venueAddress: GetVenueAddressResponseModel[] = [
  venueAddressFactory(1, {
    city: 'London',
  }),
  venueAddressFactory(1, {
    city: 'New York',
  }),
]

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
  apiNew: {
    getBookingsCsv: vi.fn(),
    getBookingsPro: vi.fn(),
    getProfile: vi.fn(),
    getUserHasBookings: vi.fn(),
    getVenueAddresses: vi.fn(),
  },
}))

vi.mock('@/commons/utils/date', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/date')),
    getToday: vi.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
  }
})

const user = sharedCurrentUserFactory()

const renderBookingsRecap = (
  overrides?: DeepPartial<RootState>,
  features?: string[]
) => {
  return renderWithProviders(null, {
    routes: individualBookingsRoutes,
    initialRouterEntries: ['/reservations'],
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: defaultGetOffererVenueResponseModel.id,
        }),
      },
      ...overrides,
    },
    features: features,
  })
}

const waitForCompleteLoading = async () => {
  await waitFor(() =>
    expect(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    ).not.toBeDisabled()
  )

  await waitFor(() => {
    expect(
      within(screen.getByLabelText('Localisation')).getAllByRole('option')
        .length
    ).toBe(3)
  })
}

describe('components | BookingsRecap | Pro user', () => {
  beforeEach(() => {
    const emptyBookingsRecapPage = {
      bookingsRecap: [],
      page: 0,
      pages: 0,
      total: 0,
    }
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue(emptyBookingsRecapPage)
    vi.spyOn(apiNew, 'getProfile').mockResolvedValue(user)
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [venueListItemFactory()],
    })
    vi.spyOn(apiNew, 'getUserHasBookings').mockResolvedValue({
      hasBookings: true,
    })
    vi.spyOn(apiNew, 'getBookingsCsv').mockResolvedValue({})
    vi.spyOn(apiNew, 'getVenueAddresses').mockResolvedValue(venueAddress)
  })

  it('should show a pre-filter section', async () => {
    renderBookingsRecap()
    await waitForCompleteLoading()

    const eventDateFilter = screen.getByLabelText('Date de l’évènement')
    const eventoffererAddressFilter = screen.getByLabelText('Localisation')
    const eventBookingPeriodFilter = screen.getByText('Période de réservation')
    expect(eventDateFilter).toBeInTheDocument()
    expect(eventoffererAddressFilter).toBeInTheDocument()
    expect(eventBookingPeriodFilter).toBeInTheDocument()
    expect(eventoffererAddressFilter).toHaveValue(
      DEFAULT_PRE_FILTERS.offererAddressId
    )
    expect(eventDateFilter).not.toHaveValue()
  })

  it('should ask user to select a pre-filter before clicking on "Rechercher"', async () => {
    renderBookingsRecap()
    await waitForCompleteLoading()

    expect(apiNew.getBookingsPro).not.toHaveBeenCalled()
    const choosePreFiltersMessage = screen.getByText(
      'Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur « Rechercher »'
    )
    expect(choosePreFiltersMessage).toBeInTheDocument()
  })

  it('should request bookings of venue requested by user when user clicks on "Rechercher"', async () => {
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(spyGetBookingsPro).toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({
          offererAddressId: venueAddress[0].id,
        }),
      })
    )
  })

  it('should warn user that his prefilters returned no booking when no bookings where returned by selected pre-filters', async () => {
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 0,
      total: 0,
      bookingsRecap: [],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    const noBookingsForPreFilters = await screen.findByText(
      'Aucune réservation trouvée pour votre recherche'
    )
    expect(noBookingsForPreFilters).toBeInTheDocument()
  })

  it('should allow user to reset its pre-filters in the no bookings warning', async () => {
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 0,
      total: 0,
      bookingsRecap: [],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    const resetButton = await screen.findByText(
      'Afficher toutes les réservations'
    )
    await userEvent.click(resetButton)

    expect(screen.getByLabelText('Localisation')).toHaveValue(
      DEFAULT_PRE_FILTERS.offererAddressId
    )
  })

  it('should not allow user to reset prefilters when none were applied', async () => {
    const bookingRecap = bookingRecapFactory()
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      bookingsRecap: [bookingRecap],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeDisabled()
  })

  it('should allow user to reset prefilters when some where applied', async () => {
    const bookingRecap = bookingRecapFactory()
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      bookingsRecap: [bookingRecap],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    const beginningPeriodInput = screen.getByLabelText('Début de la période')
    const endingPeriodInput = screen.getByLabelText('Fin de la période')
    expect(beginningPeriodInput).toHaveDisplayValue(['2020-05-16'])
    expect(endingPeriodInput).toHaveDisplayValue(['2020-06-15'])

    await userEvent.type(beginningPeriodInput, '2019-01-01')
    await userEvent.type(endingPeriodInput, '2019-02-01')
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    const resetButton = await screen.findByRole('button', {
      name: 'Réinitialiser les filtres',
    })
    await userEvent.click(resetButton)

    expect(screen.getByLabelText('Localisation')).toHaveValue(
      DEFAULT_PRE_FILTERS.offererAddressId
    )

    await waitFor(() =>
      expect(beginningPeriodInput).toHaveDisplayValue(['2020-05-16'])
    )
    expect(endingPeriodInput).toHaveDisplayValue(['2020-06-15'])
  })

  it('should ask user to select a pre-filter when user reset them', async () => {
    const bookingRecap = bookingRecapFactory()
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      bookingsRecap: [bookingRecap],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    const resetButton = await screen.findByText('Réinitialiser les filtres')
    await userEvent.click(resetButton)

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: 'Réinitialiser les filtres' })
      ).toBeDisabled()
    })
    expect(
      screen.queryByText(
        'Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur « Rechercher »'
      )
    ).toBeInTheDocument()
  })

  it('should fetch bookings for the filtered venue as many times as the number of pages', async () => {
    const bookings1 = bookingRecapFactory()
    const bookings2 = bookingRecapFactory()
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 2,
      total: 2,
      bookingsRecap: [bookings1],
    }
    const secondPaginatedBookingRecapReturned = {
      page: 2,
      pages: 2,
      total: 2,
      bookingsRecap: [bookings2],
    }
    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
      .mockResolvedValueOnce(secondPaginatedBookingRecapReturned)

    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    expect(
      await screen.findByText(bookings2.stock.offerName)
    ).toBeInTheDocument()

    expect(screen.getByText(bookings1.stock.offerName)).toBeInTheDocument()

    expect(apiNew.getBookingsPro).toHaveBeenCalledTimes(2)
    expect(spyGetBookingsPro).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        query: expect.objectContaining({
          page: 1,
          offererAddressId: venueAddress[0].id,
        }),
      })
    )
    expect(spyGetBookingsPro).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        query: expect.objectContaining({
          page: 2,
          offererAddressId: venueAddress[0].id,
        }),
      })
    )
  })

  it('should request bookings of event date requested by user when user clicks on "Afficher"', async () => {
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement'),
      '2020-06-08'
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)

    expect(spyGetBookingsPro).toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({
          eventDate: formatBrowserTimezonedDateAsUTC(
            new Date(2020, 5, 8),
            FORMAT_ISO_DATE_ONLY
          ),
        }),
      })
    )
  })

  it('should set booking period to null when user select event date', async () => {
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement'),
      '2020-08-10'
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(spyGetBookingsPro).toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({
          bookingPeriodEndingDate: undefined,
          bookingPeriodBeginningDate: undefined,
        }),
      })
    )
  })

  it('should request bookings of default period when user clicks on "Afficher" without selecting a period', async () => {
    const bookingRecap = bookingRecapFactory()

    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(spyGetBookingsPro).toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({
          bookingPeriodBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
          bookingPeriodEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
        }),
      })
    )
  })

  it('should request bookings of selected period when user clicks on "Afficher"', async () => {
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    renderBookingsRecap()
    await waitForCompleteLoading()

    const beginningPeriodInput = screen.getByLabelText('Début de la période')
    const endingPeriodInput = screen.getByLabelText('Fin de la période')

    await userEvent.clear(beginningPeriodInput)
    await userEvent.clear(endingPeriodInput)
    await userEvent.type(beginningPeriodInput, '2020-05-10')
    await userEvent.type(endingPeriodInput, '2020-06-05')
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(spyGetBookingsPro).toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({
          bookingPeriodBeginningDate: '2020-05-10',
          bookingPeriodEndingDate: '2020-06-05',
        }),
      })
    )
  })

  it('should reset bookings recap list when applying filters', async () => {
    const booking = bookingRecapFactory()
    const otherVenueBooking = bookingRecapFactory()
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookingsRecap: [booking],
    }
    const otherVenuePaginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookingsRecap: [otherVenueBooking],
    }
    vi.spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValueOnce(otherVenuePaginatedBookingRecapReturned)
      .mockResolvedValueOnce(paginatedBookingRecapReturned)

    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      ALL_OFFERER_ADDRESS_OPTION.label
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    expect(await screen.findByText(booking.stock.offerName)).toBeInTheDocument()
    expect(
      screen.queryByText(otherVenueBooking.stock.offerName)
    ).not.toBeInTheDocument()
  })

  it('should show notification with information message when there are more than 10 pages', async () => {
    const bookingsRecap = { pages: 11, bookingsRecap: [], total: 11 }
    vi.spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValueOnce({ ...bookingsRecap, page: 1 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 2 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 3 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 4 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 5 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 6 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 7 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 8 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 9 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 10 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 11 })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    const informationalMessage = await screen.findByText(
      'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
    )
    expect(informationalMessage).toBeInTheDocument()
    expect(apiNew.getBookingsPro).toHaveBeenCalledTimes(10)
  })

  it('should not show notification with information message when there are 10 pages or less', async () => {
    const bookingsRecap = { pages: 10, bookingsRecap: [], total: 10 }
    vi.spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValueOnce({ ...bookingsRecap, page: 1 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 2 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 3 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 4 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 5 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 6 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 7 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 8 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 9 })
      .mockResolvedValueOnce({ ...bookingsRecap, page: 10 })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await waitFor(() => expect(apiNew.getBookingsPro).toHaveBeenCalledTimes(10))
    const informationalMessage = screen.queryByText(
      'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
    )
    expect(informationalMessage).not.toBeInTheDocument()
  })

  it('should inform the user that the filters have been modified when at least one of them was and before clicking on the "Afficher" button', async () => {
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      'ma venue - 1 Rue de paris 75001 New York'
    )

    const informationalMessage = await screen.findByTestId(
      'refresh-required-message'
    )
    expect(informationalMessage).toBeInTheDocument()
  })

  it('should not inform the user when the selected filter is the same than the actual filter', async () => {
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      'ma venue - 1 Rue de paris 75001 New York'
    )

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      screen.getByText(ALL_OFFERER_ADDRESS_OPTION.label)
    )

    const informationalMessage = screen.queryByText(
      'Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour actualiser votre recherche.'
    )
    expect(informationalMessage).not.toBeInTheDocument()
  })

  it('should not inform the user of pre-filter modifications before first click on "Afficher" button', async () => {
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      'ma venue - 1 Rue de paris 75001 New York'
    )

    const informationalMessage = screen.queryByText(
      'Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour actualiser votre recherche.'
    )
    expect(informationalMessage).not.toBeInTheDocument()
  })

  it('should display no booking screen when user does not have any booking yet', async () => {
    vi.spyOn(apiNew, 'getUserHasBookings').mockResolvedValue({
      hasBookings: false,
    })

    renderBookingsRecap()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('button', {
        name: 'Rechercher les réservations',
      })
    ).toBeDisabled()
    expect(
      await screen.findByText('Vous n’avez aucune réservation pour le moment')
    ).toBeInTheDocument()
  })
  it('should not render downloads moved banner or filters without search', async () => {
    renderBookingsRecap()
    await waitForCompleteLoading()

    expect(
      screen.queryByText(
        'Télécharger vos réservations dans l’onglet “Données d’activité” de votre Espace administration accessible en haut à droite.'
      )
    ).not.toBeInTheDocument()

    expect(screen.queryByLabelText('Critère')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Recherche')).not.toBeInTheDocument()
  })

  it('should render downloads moved banner and filters after search', async () => {
    const bookingRecap = bookingRecapFactory()
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      bookingsRecap: [bookingRecap],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)

    expect(
      screen.queryByText(
        'Télécharger vos réservations dans l’onglet “Données d’activité” de votre Espace administration accessible en haut à droite.'
      )
    ).toBeInTheDocument()
  })

  it('should fetch bookings using venueId when clicking "Afficher"', async () => {
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = vi
      .spyOn(apiNew, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(spyGetBookingsPro).toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({
          page: 1,
        }),
      })
    )
  })

  it('should reset filters to venue-scoped defaults', async () => {
    vi.spyOn(apiNew, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 0,
      total: 0,
      bookingsRecap: [],
    })
    renderBookingsRecap()
    await waitForCompleteLoading()

    await userEvent.selectOptions(
      screen.getByLabelText('Localisation'),
      venueAddress[0].id.toString()
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Rechercher les réservations' })
    )

    const resetButton = await screen.findByText(
      'Afficher toutes les réservations'
    )
    await userEvent.click(resetButton)

    expect(screen.getByLabelText('Localisation')).toHaveValue(
      DEFAULT_PRE_FILTERS.offererAddressId
    )
  })
})
