import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import type { RouteObject } from 'react-router'

import { api } from '@/apiClient/api'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { offererAddressFactory } from '@/commons/utils/factories/offererAddressFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdministrationLayout } from '@/layouts/AdministrationLayout/AdministrationLayout'

import { Component as IndividualActivityData } from './IndividualActivityData'

vi.mock('@/apiClient/api', () => ({
  api: {
    getBookingsCsv: vi.fn(),
    getOffererAddresses: vi.fn(),
  },
}))
const mockLogEvent = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: mockLogEvent }),
}))
vi.mock('@/commons/hooks/swr/useOffererNamesQuery', () => ({
  useOffererNamesQuery: () => ({ isLoading: false }),
}))
vi.mock('@/commons/utils/date', async () => ({
  ...(await vi.importActual('@/commons/utils/date')),
  getToday: vi.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
}))

const user = sharedCurrentUserFactory()
const offererAddresses = [
  offererAddressFactory({ label: 'Adresse principale' }),
  offererAddressFactory({ city: 'Lyon' }),
]

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

const renderIndividualActivityData = () => {
  renderWithProviders(null, {
    routes,
    initialRouterEntries: ['/administration/donnees-activite/individuel'],
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedAdminOfferer: defaultGetOffererResponseModel,
      },
      offerer: {
        offererNames: [defaultGetOffererResponseModel],
        currentOfferer: defaultGetOffererResponseModel,
      },
    },
  })
}

describe('IndividualActivityData', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererAddresses').mockResolvedValue(offererAddresses)
  })

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

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_RESET_FILTERS, {
      from: '/administration/donnees-activite/individuel',
    })
  })

  it('should pass admin offerer id to CSV download', async () => {
    vi.spyOn(api, 'getBookingsCsv').mockResolvedValue({})
    renderIndividualActivityData()

    await userEvent.click(
      screen.getByRole('button', { name: 'Télécharger les réservations' })
    )
    const downloadSubButton = await screen.findByRole('menuitem', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(downloadSubButton)

    expect(api.getBookingsCsv).toHaveBeenCalledWith(
      1,
      defaultGetOffererResponseModel.id,
      null,
      null,
      null,
      DEFAULT_PRE_FILTERS.bookingStatusFilter,
      DEFAULT_PRE_FILTERS.bookingBeginningDate,
      DEFAULT_PRE_FILTERS.bookingEndingDate,
      null
    )
  })
})
