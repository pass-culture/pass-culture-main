import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  SharedCurrentUserResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
import * as pcapi from 'repository/pcapi/pcapi'
import {
  bookingRecapFactory,
  getVenueListItemFactory,
} from 'utils/apiFactories'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import BookingsRecapContainer from '../Bookings'

jest.mock('repository/pcapi/pcapi', () => ({
  getFilteredBookingsCSV: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
    getBookingsPro: jest.fn(),
    getVenues: jest.fn(),
    getUserHasBookings: jest.fn(),
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
  storeOverrides: any,
  initialEntries = '/reservations',
  waitDomReady?: boolean
) => {
  const rtlReturn = renderWithProviders(
    <>
      <BookingsRecapContainer />
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: [initialEntries] }
  )

  const { hasBookings } = await api.getUserHasBookings()
  const displayBookingsButton = screen.getByRole('button', { name: 'Afficher' })
  const downloadBookingsCsvButton = screen.getByRole('button', {
    name: 'Télécharger',
  })

  const submitFilters = async () => {
    await userEvent.click(displayBookingsButton)
  }
  const submitDownloadFilters = async () => {
    await userEvent.click(downloadBookingsCsvButton)
  }

  if (waitDomReady || waitDomReady === undefined) {
    if (hasBookings) {
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
  let venue: VenueListItemResponseModel
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
      isAdmin: false,
      email: 'rené@example.com',
    } as SharedCurrentUserResponseModel
    store = {
      user: {
        currentUser: user,
      },
    }
    jest.spyOn(api, 'getProfile').mockResolvedValue(user)
    venue = getVenueListItemFactory({})
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [venue] })
    jest
      .spyOn(api, 'getUserHasBookings')
      .mockResolvedValue({ hasBookings: true })
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
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(
      spyGetBookingsPro.mock.calls[0][NTH_ARGUMENT_GET_BOOKINGS.venueId - 1]
    ).toBe(venue.nonHumanizedId.toString())
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
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    await submitFilters()

    // When
    const resetButton = screen.getByText('réinitialiser tous les filtres.')
    await userEvent.click(resetButton)

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
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    const defaultBookingPeriodBeginningDateInput = '16/05/2020'
    const defaultBookingPeriodEndingDateInput = '15/06/2020'
    const bookingPeriodBeginningDateInput = screen.getByDisplayValue(
      defaultBookingPeriodBeginningDateInput
    )
    await userEvent.click(bookingPeriodBeginningDateInput)
    await userEvent.click(screen.getAllByText('5')[0])
    const bookingPeriodEndingDateInput = screen.getByDisplayValue(
      defaultBookingPeriodEndingDateInput
    )
    await userEvent.click(bookingPeriodEndingDateInput)
    await userEvent.click(screen.getAllByText('5')[0])
    await submitFilters()

    // When
    const resetButton = await screen.findByText('Réinitialiser les filtres')
    await userEvent.click(resetButton)

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
      bookingsRecap: [bookingRecap],
    })
    const { submitFilters } = await renderBookingsRecap(store)
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    await submitFilters()

    // When
    const resetButton = await screen.findByText('Réinitialiser les filtres')
    await userEvent.click(resetButton)

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
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')

      .mockResolvedValueOnce(paginatedBookingRecapReturned)

      .mockResolvedValueOnce(secondPaginatedBookingRecapReturned)
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    await submitFilters()

    // Then
    const secondBookingRecap = await screen.findAllByText(
      bookings2.stock.offerName
    )
    expect(secondBookingRecap).toHaveLength(2)
    const firstBookingRecap = screen.getAllByText(bookings1.stock.offerName)
    expect(firstBookingRecap).toHaveLength(2)

    expect(api.getBookingsPro).toHaveBeenCalledTimes(2)
    expect(
      spyGetBookingsPro.mock.calls[0][NTH_ARGUMENT_GET_BOOKINGS.page - 1]
    ).toBe(1)
    expect(
      spyGetBookingsPro.mock.calls[0][NTH_ARGUMENT_GET_BOOKINGS.venueId - 1]
    ).toBe(venue.nonHumanizedId.toString())
    expect(
      spyGetBookingsPro.mock.calls[1][NTH_ARGUMENT_GET_BOOKINGS.page - 1]
    ).toBe(2)
    expect(
      spyGetBookingsPro.mock.calls[1][NTH_ARGUMENT_GET_BOOKINGS.venueId - 1]
    ).toBe(venue.nonHumanizedId.toString())
  })

  it('should request bookings of event date requested by user when user clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await userEvent.click(screen.getByLabelText('Date de l’évènement'))
    await userEvent.click(screen.getByText('8'))
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(
      spyGetBookingsPro.mock.calls[0][NTH_ARGUMENT_GET_BOOKINGS.eventDate - 1]
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
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await userEvent.click(screen.getByLabelText('Date de l’évènement'))
    await userEvent.click(screen.getByText('8'))
    await submitFilters()
    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate - 1
      ]
    ).toBeUndefined()
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate - 1
      ]
    ).toBeUndefined()
  })

  it('should request bookings of default period when user clicks on "Afficher" without selecting a period', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()

    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)

    // When
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate - 1
      ]
    ).toStrictEqual(FORMATTED_DEFAULT_BEGINNING_DATE)
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate - 1
      ]
    ).toStrictEqual(FORMATTED_DEFAULT_ENDING_DATE)
  })

  it('should request bookings of selected period when user clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)

    const beginningPeriodInput = screen.getByTestId(
      'period-filter-begin-picker'
    )
    const endingPeriodInput = screen.getByTestId('period-filter-end-picker')

    // When
    await userEvent.click(beginningPeriodInput)
    await userEvent.click(screen.getByText('10'))
    await userEvent.click(endingPeriodInput)
    await userEvent.click(screen.getAllByText('5')[0])
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate - 1
      ]
    ).toStrictEqual(
      formatBrowserTimezonedDateAsUTC(
        new Date(2020, 4, 10),
        FORMAT_ISO_DATE_ONLY
      )
    )
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate - 1
      ]
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
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)

    const beginningPeriodInput = screen.getByTestId(
      'period-filter-begin-picker'
    )
    const endingPeriodInput = screen.getByTestId('period-filter-end-picker')

    await userEvent.click(endingPeriodInput)
    await userEvent.click(screen.getByText('12'))

    // When
    await userEvent.clear(beginningPeriodInput)
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    const thirtyDaysBeforeEndingDate = formatBrowserTimezonedDateAsUTC(
      new Date(2020, 4, 13),
      FORMAT_ISO_DATE_ONLY
    )
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingBeginningDate - 1
      ]
    ).toStrictEqual(thirtyDaysBeforeEndingDate)
  })

  it('should set default ending period date when user empties it and clicks on "Afficher"', async () => {
    // Given
    const bookingRecap = bookingRecapFactory()
    const spyGetBookingsPro = jest
      .spyOn(api, 'getBookingsPro')
      .mockResolvedValue({
        page: 1,
        pages: 1,
        total: 1,
        bookingsRecap: [bookingRecap],
      })
    const { submitFilters } = await renderBookingsRecap(store)
    const beginningPeriodInput = screen.getByTestId(
      'period-filter-begin-picker'
    )
    const endingPeriodInput = screen.getByTestId('period-filter-end-picker')
    await userEvent.click(beginningPeriodInput)
    await userEvent.click(screen.getByText('10'))

    // When
    await userEvent.clear(endingPeriodInput)
    await submitFilters()

    // Then
    await screen.findAllByText(bookingRecap.stock.offerName)
    const thirtyDaysAfterBeginningDate = formatBrowserTimezonedDateAsUTC(
      new Date(2020, 5, 9),
      FORMAT_ISO_DATE_ONLY
    )
    expect(
      spyGetBookingsPro.mock.calls[0][
        NTH_ARGUMENT_GET_BOOKINGS.bookingEndingDate - 1
      ]
    ).toStrictEqual(thirtyDaysAfterBeginningDate)
  })

  it('should reset bookings recap list when applying filters', async () => {
    // Given
    const booking = bookingRecapFactory()
    const otherVenueBooking = bookingRecapFactory()
    const otherVenue = getVenueListItemFactory()
    jest
      .spyOn(api, 'getVenues')
      .mockResolvedValue({ venues: [venue, otherVenue] })
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

      .mockResolvedValueOnce(otherVenuePaginatedBookingRecapReturned)

      .mockResolvedValueOnce(paginatedBookingRecapReturned)
    const { submitFilters } = await renderBookingsRecap(store)

    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      otherVenue.nonHumanizedId.toString()
    )
    await submitFilters()
    await screen.findAllByText(otherVenueBooking.stock.offerName)

    // When
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    await submitFilters()

    // Then
    const firstBookingRecap = await screen.findAllByText(
      booking.stock.offerName
    )
    expect(firstBookingRecap).toHaveLength(2)
    expect(
      screen.queryByText(otherVenueBooking.stock.offerName)
    ).not.toBeInTheDocument()
  })

  it('should show notification with information message when there are more than 5 pages', async () => {
    // Given
    const bookingsRecap = { pages: 6, bookingsRecap: [] }
    jest
      .spyOn(api, 'getBookingsPro')
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 1 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 2 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 3 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 4 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 5 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 6 })
    await renderBookingsRecap(store)

    // when
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
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
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 1 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 2 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 3 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 4 })
      // @ts-expect-error FIX ME
      .mockResolvedValueOnce({ ...bookingsRecap, page: 5 })
    await renderBookingsRecap(store)

    // when
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.nonHumanizedId.toString()
    )
    await userEvent.click(screen.getByText('Afficher', { selector: 'button' }))

    // Then
    expect(api.getBookingsPro).toHaveBeenCalledTimes(5)
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
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.publicName ?? venue.name
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
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.publicName ?? venue.name
    )

    // When
    await userEvent.selectOptions(
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
    await userEvent.selectOptions(
      screen.getByLabelText('Lieu'),
      venue.publicName ?? venue.name
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
      .spyOn(api, 'getUserHasBookings')
      .mockResolvedValue({ hasBookings: false })
    await renderBookingsRecap(store)

    //Then
    const displayBookingsButton = screen.getByRole('button', {
      name: 'Afficher',
    })
    const downloadBookingsCsvButton = screen.getByRole('button', {
      name: 'Télécharger',
    })
    const informationMessage = await screen.findByText(
      'Vous n’avez aucune réservation pour le moment'
    )

    expect(displayBookingsButton).toBeDisabled()
    expect(downloadBookingsCsvButton).toBeDisabled()
    expect(informationMessage).toBeInTheDocument()
  })
})
