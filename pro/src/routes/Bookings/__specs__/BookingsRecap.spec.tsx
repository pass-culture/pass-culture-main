import '@testing-library/jest-dom'

import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { bookingRecapFactory, venueFactory } from 'utils/apiFactories'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'
import { getNthCallNthArg } from 'utils/testHelpers'

import BookingsRecapContainer, { BookingsRouterState } from '../Bookings'

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
  getFilteredBookingsCSV: jest.fn(),
  getUserHasBookings: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
    getBookingsPro: jest.fn(),
  },
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
}))
const FORMATTED_DEFAULT_BEGINNING_DATE = formatBrowserTimezonedDateAsUTC(
  DEFAULT_PRE_FILTERS.bookingBeginningDate,
  FORMAT_ISO_DATE_ONLY
)
const FORMATTED_DEFAULT_ENDING_DATE = formatBrowserTimezonedDateAsUTC(
  DEFAULT_PRE_FILTERS.bookingEndingDate,
  FORMAT_ISO_DATE_ONLY
)
const NTH_ARGUMENT_GET_BOOKINGS = {
  page: 1,
  venueId: 2,
  eventDate: 3,
  bookingBeginningDate: 5,
  bookingEndingDate: 6,
}

const renderBookingsRecap = async (
  store: any,
  routerState?: BookingsRouterState,
  waitDomReady?: boolean
) => {
  const rtlReturn = render(
    <Provider store={configureTestStore(store)}>
      <MemoryRouter
        initialEntries={[{ pathname: '/reservations', state: routerState }]}
      >
        <BookingsRecapContainer />
        <NotificationContainer />
      </MemoryRouter>
    </Provider>
  )

  const { hasBoookings } = await pcapi.getUserHasBookings()
  const displayBookingsButton = screen.getByRole('button', { name: 'Afficher' })
  const downloadBookingsCsvButton = screen.getByRole('button', {
    name: 'Télécharger',
  })

  const submitFilters = async () => {
    fireEvent.click(displayBookingsButton)
    await waitFor(() => expect(displayBookingsButton).not.toBeDisabled())
  }
  const submitDownloadFilters = async () => {
    await userEvent.click(downloadBookingsCsvButton)
  }

  if (waitDomReady || waitDomReady === undefined) {
    if (hasBoookings) {
      await waitFor(() => expect(displayBookingsButton).not.toBeDisabled())
    } else {
      const loadingMessage = screen.queryByText('Chargement en cours ...')
      await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())
    }
  }

  return {
    rtlReturn,
    submitDownloadFilters,
    submitFilters,
  }
}

describe('components | BookingsRecap | Pro user', () => {
  let store: any
  let venue: { id: string; name: string; publicName: string }
  let user

  beforeEach(() => {
    const emptyBookingsRecapPage = {
      bookingsRecap: [],
      page: 0,
      pages: 0,
      total: 0,
    }
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue(emptyBookingsRecapPage)

    user = {
      publicName: 'René',
      isAdmin: false,
      email: 'rené@example.com',
    } as SharedCurrentUserResponseModel
    store = {
      user: {
        currentUser: user,
      },
    }
    jest.spyOn(api, 'getProfile').mockResolvedValue(user)
    venue = venueFactory()
    jest.spyOn(pcapi, 'getVenuesForOfferer').mockResolvedValue([venue])
    jest
      .spyOn(pcapi, 'getUserHasBookings')
      .mockResolvedValue({ hasBookings: true })
  })

  afterEach(() => {
    jest.spyOn(api, 'getBookingsPro').mockReset()
  })

  it('should show a pre-filter section', async () => {
    // When
    await renderBookingsRecap(store)

    // Then
    const eventDateFilter = screen.getByLabelText('Date de l’évènement')
    const eventVenueFilter = screen.getByLabelText('Lieu')
    const eventBookingPeriodFilter = screen.getByText('Période de réservation')
    expect(eventDateFilter).toBeInTheDocument()
    expect(eventVenueFilter).toBeInTheDocument()
    expect(eventBookingPeriodFilter).toBeInTheDocument()
    expect(eventVenueFilter).toHaveValue(DEFAULT_PRE_FILTERS.offerVenueId)
    expect(eventDateFilter).not.toHaveValue()
  })

  it('should ask user to select a pre-filter before clicking on "Afficher"', async () => {
    // When
    await renderBookingsRecap(store)

    // Then
    expect(api.getBookingsPro).not.toHaveBeenCalled()
    const choosePreFiltersMessage = screen.getByText(
      'Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur « Afficher »'
    )
    expect(choosePreFiltersMessage).toBeInTheDocument()
  })

  it('should request bookings of venue requested by user when user clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    expect(
      getNthCallNthArg(api.getBookingsPro, 1, NTH_ARGUMENT_GET_BOOKINGS.venueId)
    ).toBe(venue.id)
  })

  it('should warn user that his prefilters returned no booking when no bookings where returned by selected pre-filters', async () => {
    // Given
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 0,
      total: 0,
      bookingsRecap: [],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await submitFilters()

    // Then
    const noBookingsForPreFilters = await screen.findByText(
      'Aucune réservation trouvée pour votre recherche.'
    )
    expect(noBookingsForPreFilters).toBeInTheDocument()
  })

  it('should allow user to reset its pre-filters in the no bookings warning', async () => {
    // Given
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 0,
      total: 0,
      bookingsRecap: [],
    })
    const { submitFilters } = await renderBookingsRecap(store)
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await submitFilters()

    // When
    const resetButton = await screen.findByText(
      'réinitialiser tous les filtres.'
    )
    fireEvent.click(resetButton)

    // Then
    expect(screen.getByLabelText('Lieu')).toHaveValue(
      DEFAULT_PRE_FILTERS.offerVenueId
    )
  })

  it('should not allow user to reset prefilters when none were applied', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await submitFilters()

    // Then
    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeDisabled()
  })

  it('should allow user to reset prefilters when some where applied', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    const defaultBookingPeriodBeginningDateInput = '16/05/2020'
    const defaultBookingPeriodEndingDateInput = '15/06/2020'
    const bookingPeriodBeginningDateInput = screen.getByDisplayValue(
      defaultBookingPeriodBeginningDateInput
    )
    fireEvent.click(bookingPeriodBeginningDateInput)
    fireEvent.click(screen.getAllByText('5')[0])
    const bookingPeriodEndingDateInput = screen.getByDisplayValue(
      defaultBookingPeriodEndingDateInput
    )
    await userEvent.click(bookingPeriodEndingDateInput)
    await userEvent.click(screen.getAllByText('5')[0])
    await submitFilters()

    // When
    const resetButton = await screen.findByText('Réinitialiser les filtres')
    fireEvent.click(resetButton)

    // Then
    expect(screen.getByLabelText('Lieu')).toHaveValue(
      DEFAULT_PRE_FILTERS.offerVenueId
    )
    await expect(
      screen.findByDisplayValue(defaultBookingPeriodBeginningDateInput)
    ).resolves.toBeInTheDocument()
    await expect(
      screen.findByDisplayValue(defaultBookingPeriodEndingDateInput)
    ).resolves.toBeInTheDocument()
  })

  it('should ask user to select a pre-filter when user reset them', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)
    await userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await submitFilters()

    // When
    const resetButton = await screen.findByText('Réinitialiser les filtres')
    fireEvent.click(resetButton)

    // Then
    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeDisabled()
    const choosePreFiltersMessage = screen.getByText(
      'Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur « Afficher »'
    )
    expect(choosePreFiltersMessage).toBeInTheDocument()
  })

  it('should have a CSV download button', async () => {
    // When
    await renderBookingsRecap(store)

    // Then
    expect(
      screen.getByRole('button', { name: 'Télécharger' })
    ).toBeInTheDocument()
  })

  it('should fetch API for CSV when clicking on the download button and disable button while its loading', async () => {
    // Given

    const { submitDownloadFilters } = await renderBookingsRecap({
      ...store,
      features: {
        list: [
          {
            isActive: true,
            name: 'ENABLE_CSV_MULTI_DOWNLOAD_BUTTON',
            nameKey: 'ENABLE_CSV_MULTI_DOWNLOAD_BUTTON',
          },
        ],
      },
    })

    // When
    // submit utils method wait for button to become disabled then enabled.
    await submitDownloadFilters()
    const downloadSubButton = await screen.findByRole('button', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(downloadSubButton)

    // Then
    expect(pcapi.getFilteredBookingsCSV).toHaveBeenCalledWith({
      bookingPeriodBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
      bookingPeriodEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
      bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
      eventDate: 'all',
      offerType: 'all',
      page: 1,
      venueId: 'all',
    })
  })

  it('should display an error message on CSV download when API returns a status other than 200', async () => {
    // Given
    jest
      .spyOn(pcapi, 'getFilteredBookingsCSV')
      .mockImplementation(() => Promise.reject(new Error('An error happened.')))

    const { submitDownloadFilters } = await renderBookingsRecap({
      ...store,
      features: {
        list: [
          {
            isActive: true,
            name: 'ENABLE_CSV_MULTI_DOWNLOAD_BUTTON',
            nameKey: 'ENABLE_CSV_MULTI_DOWNLOAD_BUTTON',
          },
        ],
      },
    })

    // When
    await submitDownloadFilters()
    const downloadSubButton = await screen.findByRole('button', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(downloadSubButton)

    // Then
    await expect(
      screen.findByText(
        'Une erreur s’est produite. Veuillez réessayer ultérieurement',
        { exact: false }
      )
    ).resolves.toBeInTheDocument()
  })

  it('should fetch bookings for the filtered venue as many times as the number of pages', async () => {
    // Given
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
    jest
      .spyOn(api, 'getBookingsPro')
      // @ts-ignore FIX ME
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
      // @ts-ignore FIX ME
      .mockResolvedValueOnce(secondPaginatedBookingRecapReturned)
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await submitFilters()

    // Then
    const secondBookingRecap = await screen.findAllByText(
      bookings2.stock.offer_name
    )
    expect(secondBookingRecap).toHaveLength(2)
    const firstBookingRecap = screen.getAllByText(bookings1.stock.offer_name)
    expect(firstBookingRecap).toHaveLength(2)

    expect(api.getBookingsPro).toHaveBeenCalledTimes(2)
    expect(
      getNthCallNthArg(api.getBookingsPro, 1, NTH_ARGUMENT_GET_BOOKINGS.page)
    ).toBe(1)
    expect(
      getNthCallNthArg(api.getBookingsPro, 1, NTH_ARGUMENT_GET_BOOKINGS.venueId)
    ).toBe(venue.id)
    expect(
      getNthCallNthArg(api.getBookingsPro, 2, NTH_ARGUMENT_GET_BOOKINGS.page)
    ).toBe(2)
    expect(
      getNthCallNthArg(api.getBookingsPro, 2, NTH_ARGUMENT_GET_BOOKINGS.venueId)
    ).toBe(venue.id)
  })

  it('should request bookings of event date requested by user when user clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    fireEvent.click(screen.getByLabelText('Date de l’évènement'))
    fireEvent.click(screen.getByText('8'))
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.eventDate
      )
    ).toStrictEqual(
      formatBrowserTimezonedDateAsUTC(
        new Date(2020, 5, 8),
        FORMAT_ISO_DATE_ONLY
      )
    )
  })

  it('should set booking period to null when user select event date', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    fireEvent.click(screen.getByLabelText('Date de l’évènement'))
    fireEvent.click(screen.getByText('8'))
    await submitFilters()
    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate
      )
    ).toBeUndefined()
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate
      )
    ).toBeUndefined()
  })

  it('should request bookings of default period when user clicks on "Afficher" without selecting a period', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()

    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate
      )
    ).toStrictEqual(FORMATTED_DEFAULT_BEGINNING_DATE)
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate
      )
    ).toStrictEqual(FORMATTED_DEFAULT_ENDING_DATE)
  })

  it('should request bookings of selected period when user clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    const bookingPeriodWrapper = screen.getByText('Période de réservation')
    const [beginningPeriodInput, endingPeriodInput] =
      within(bookingPeriodWrapper).getAllByPlaceholderText('JJ/MM/AAAA')

    // When
    fireEvent.click(beginningPeriodInput)
    fireEvent.click(screen.getByText('10'))
    fireEvent.click(endingPeriodInput)
    fireEvent.click(screen.getAllByText('5')[0])
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate
      )
    ).toStrictEqual(
      formatBrowserTimezonedDateAsUTC(
        new Date(2020, 4, 10),
        FORMAT_ISO_DATE_ONLY
      )
    )
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate
      )
    ).toStrictEqual(
      formatBrowserTimezonedDateAsUTC(
        new Date(2020, 5, 5),
        FORMAT_ISO_DATE_ONLY
      )
    )
  })

  it('should set default beginning period date when user empties it and clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    const bookingPeriodWrapper = screen.getByText('Période de réservation')
    const [beginningPeriodInput, endingPeriodInput] =
      within(bookingPeriodWrapper).getAllByPlaceholderText('JJ/MM/AAAA')
    fireEvent.click(endingPeriodInput)
    fireEvent.click(screen.getByText('12'))

    // When
    fireEvent.change(beginningPeriodInput, { target: { value: '' } })
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    const thirtyDaysBeforeEndingDate = formatBrowserTimezonedDateAsUTC(
      new Date(2020, 4, 13),
      FORMAT_ISO_DATE_ONLY
    )
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate
      )
    ).toStrictEqual(thirtyDaysBeforeEndingDate)
  })

  it('should set default ending period date when user empties it and clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    const bookingPeriodWrapper = screen.getByText('Période de réservation')
    const [beginningPeriodInput, endingPeriodInput] =
      within(bookingPeriodWrapper).getAllByPlaceholderText('JJ/MM/AAAA')
    fireEvent.click(beginningPeriodInput)
    fireEvent.click(screen.getByText('10'))

    // When
    fireEvent.change(endingPeriodInput, { target: { value: '' } })
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    const thirtyDaysAfterBeginningDate = formatBrowserTimezonedDateAsUTC(
      new Date(2020, 5, 9),
      FORMAT_ISO_DATE_ONLY
    )
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate
      )
    ).toStrictEqual(thirtyDaysAfterBeginningDate)
  })

  it('should not be possible to select ending period date greater than today', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    jest.spyOn(api, 'getBookingsPro').mockResolvedValue({
      page: 1,
      pages: 1,
      total: 1,
      // @ts-ignore FIX ME
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)

    const bookingPeriodWrapper = screen.getByText('Période de réservation')
    const endingPeriodInput =
      within(bookingPeriodWrapper).getAllByPlaceholderText('JJ/MM/AAAA')[1]

    // When
    fireEvent.click(endingPeriodInput)
    fireEvent.click(screen.getByText('16'))
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offer_name)
    expect(
      getNthCallNthArg(
        api.getBookingsPro,
        1,
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate
      )
    ).toStrictEqual(FORMATTED_DEFAULT_ENDING_DATE)
  })

  it('should reset bookings recap list when applying filters', async () => {
    // Given
    const booking = bookingRecapFactory()
    const otherVenueBooking = bookingRecapFactory()
    const otherVenue = venueFactory()
    jest
      .spyOn(pcapi, 'getVenuesForOfferer')
      .mockResolvedValue([venue, otherVenue])
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
    jest
      .spyOn(api, 'getBookingsPro')
      // @ts-ignore FIX ME
      .mockResolvedValueOnce(otherVenuePaginatedBookingRecapReturned)
      // @ts-ignore FIX ME
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
    const { submitFilters } = await renderBookingsRecap(store)

    userEvent.selectOptions(screen.getByLabelText('Lieu'), otherVenue.id)
    await submitFilters()
    await screen.findAllByText(otherVenueBooking.stock.offer_name)

    // When
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await submitFilters()

    // Then
    const firstBookingRecap = await screen.findAllByText(
      booking.stock.offer_name
    )
    expect(firstBookingRecap).toHaveLength(2)
    expect(
      screen.queryByText(otherVenueBooking.stock.offer_name)
    ).not.toBeInTheDocument()
  })

  it('should show notification with information message when there are more than 5 pages', async () => {
    // Given
    const bookingsRecap = { pages: 6, bookingsRecap: [] }
    jest
      .spyOn(api, 'getBookingsPro')
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 1 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 2 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 3 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 4 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 5 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 6 })
    await renderBookingsRecap(store)

    // when
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await userEvent.click(screen.getByText('Afficher', { selector: 'button' }))

    // Then
    const informationalMessage = await screen.findByText(
      'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
    )
    expect(informationalMessage).toBeInTheDocument()
    expect(api.getBookingsPro).toHaveBeenCalledTimes(5)
  })

  it('should not show notification with information message when there are 5 pages or less', async () => {
    // Given
    const bookingsRecap = { pages: 5, bookingsRecap: [] }
    jest
      .spyOn(api, 'getBookingsPro')
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 1 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 2 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 3 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 4 })
      // @ts-ignore FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 5 })
    await renderBookingsRecap(store)

    // when
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await userEvent.click(screen.getByText('Afficher', { selector: 'button' }))

    // Then
    await waitFor(() => expect(api.getBookingsPro).toHaveBeenCalledTimes(5))
    const informationalMessage = screen.queryByText(
      'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
    )
    expect(informationalMessage).not.toBeInTheDocument()
  })

  it('should inform the user that the filters have been modified when at least one of them was and before clicking on the "Afficher" button', async () => {
    // Given
    const { submitFilters } = await renderBookingsRecap(store)
    await submitFilters()

    // When
    userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      await screen.findByText(venue.publicName)
    )

    // Then
    const informationalMessage = await screen.findByTestId(
      'refresh-required-message'
    )
    expect(informationalMessage).toBeInTheDocument()
  })

  it('should not inform the user when the selected filter is the same than the actual filter', async () => {
    // Given
    await renderBookingsRecap(store)
    userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      await screen.findByText(venue.publicName)
    )

    // When
    userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      screen.getByText('Tous les lieux')
    )

    // Then
    const informationalMessage = screen.queryByText(
      'Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour actualiser votre recherche.'
    )
    expect(informationalMessage).not.toBeInTheDocument()
  })

  it('should not inform the user of pre-filter modifications before first click on "Afficher" button', async () => {
    // Given
    await renderBookingsRecap(store)

    // When
    userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      await screen.findByText(venue.publicName)
    )

    // Then
    const informationalMessage = screen.queryByText(
      'Vos filtres ont été modifiés. Veuillez cliquer sur « Afficher » pour actualiser votre recherche.'
    )
    expect(informationalMessage).not.toBeInTheDocument()
  })

  it('should display no booking screen when user does not have any booking yet', async () => {
    //Given
    jest
      .spyOn(pcapi, 'getUserHasBookings')
      .mockResolvedValue({ hasBookings: false })
    await renderBookingsRecap(store)

    //Then
    const displayBookingsButton = screen.getByRole('button', {
      name: 'Afficher',
    })
    const downloadBookingsCsvButton = screen.getByRole('button', {
      name: 'Télécharger',
    })
    const informationMessage = screen.queryByText(
      'Vous n’avez aucune réservation pour le moment'
    )

    expect(displayBookingsButton).toBeDisabled()
    expect(downloadBookingsCsvButton).toBeDisabled()
    expect(informationMessage).toBeInTheDocument()
  })
})
