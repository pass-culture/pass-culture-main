import { act, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import type { RouteObject } from 'react-router'

import { apiNew } from '@/apiClient/api'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { setSelectedAdminOfferer } from '@/commons/store/user/reducer'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  makeUserSliceState,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdministrationLayout } from '@/layouts/AdministrationLayout/AdministrationLayout'

import { Component as IndividualActivityData } from './IndividualActivityData'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getBookingsCsv: vi.fn(),
    getBookingsExcel: vi.fn(),
  },
}))
const mockLogEvent = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: mockLogEvent }),
}))
vi.mock('@/commons/hooks/swr/useOffererNamesQuery', () => ({
  useOffererNamesQuery: () => ({ isLoading: false, data: [] }),
}))
vi.mock('@/commons/utils/date', async () => ({
  ...(await vi.importActual('@/commons/utils/date')),
  getToday: vi.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
}))

const user = sharedCurrentUserFactory()

const routes: RouteObject[] = [
  {
    path: '/administration',
    Component: AdministrationLayout,
    children: [
      {
        path: 'donnees-activite/individuel',
        handle: { title: "Données d'activité : individuel" },
        element: <IndividualActivityData />,
      },
    ],
  },
]

const renderIndividualActivityData = () =>
  renderWithProviders(null, {
    routes,
    initialRouterEntries: ['/administration/donnees-activite/individuel'],
    user,
    storeOverrides: {
      user: makeUserSliceState({
        currentUser: user,
        selectedAdminOfferer: defaultGetOffererResponseModel,
        offererNames: [
          getOffererNameFactory({ id: defaultGetOffererResponseModel.id }),
          getOffererNameFactory({ id: 2 }),
        ],
      }),
    },
  })

describe('IndividualActivityData', () => {
  it('should render the subtitle', () => {
    renderIndividualActivityData()

    expect(
      screen.getByText('Téléchargement des réservations individuelles')
    ).toBeInTheDocument()
  })

  it('should render the pre-filters form without the "Afficher" button', () => {
    renderIndividualActivityData()

    expect(
      screen.getByRole('button', { name: 'Télécharger les réservations' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Afficher' })
    ).not.toBeInTheDocument()
  })

  it('should log CLICKED_RESET_FILTERS event when resetting filters', async () => {
    renderIndividualActivityData()

    const eventDateInput = screen.getByLabelText('Date de l\u2019évènement')
    await userEvent.type(eventDateInput, '2020-06-08')

    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_RESET_FILTERS)
  })

  it('should pass admin offerer id to CSV download', async () => {
    vi.spyOn(apiNew, 'getBookingsCsv').mockResolvedValue({})
    renderIndividualActivityData()

    await userEvent.click(
      screen.getByRole('button', { name: 'Télécharger les réservations' })
    )
    const downloadSubButton = await screen.findByRole('menuitem', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(downloadSubButton)

    expect(apiNew.getBookingsCsv).toHaveBeenCalledWith({
      query: {
        offererId: defaultGetOffererResponseModel.id,
        page: 1,
        offerId: null,
        eventDate: null,
        bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
        bookingPeriodBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
        bookingPeriodEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
        offererAddressId: null,
      },
    })
  })

  it('should reset filters when the selected offerer changes', async () => {
    const secondOfferer = { ...defaultGetOffererResponseModel, id: 2 }

    const { store } = renderIndividualActivityData()

    const eventDateInput = screen.getByLabelText('Date de l\u2019évènement')
    await userEvent.type(eventDateInput, '2020-06-08')

    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeEnabled()

    act(() => {
      store.dispatch(setSelectedAdminOfferer(secondOfferer))
    })

    expect(screen.getByLabelText('Date de l\u2019évènement')).toHaveValue('')
  })

  it('should track download clicks', async () => {
    vi.spyOn(apiNew, 'getBookingsCsv').mockResolvedValue({})
    vi.spyOn(apiNew, 'getBookingsExcel').mockResolvedValue({})
    renderIndividualActivityData()

    await userEvent.click(
      screen.getByRole('button', { name: 'Télécharger les réservations' })
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_ADMIN_DOWNLOAD_BOOKINGS
    )

    await userEvent.click(
      screen.getByRole('menuitem', { name: 'Microsoft Excel (.xls)' })
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_ADMIN_DOWNLOAD_BOOKINGS_XLS
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Télécharger les réservations' })
    )
    await userEvent.click(
      screen.getByRole('menuitem', { name: 'Fichier CSV (.csv)' })
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_ADMIN_DOWNLOAD_BOOKINGS_CSV
    )
  })
})
