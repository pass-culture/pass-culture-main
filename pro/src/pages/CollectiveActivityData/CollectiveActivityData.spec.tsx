import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import type { RouteObject } from 'react-router'

import { api } from '@/apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import { AdministrationLayout } from '@/layouts/AdministrationLayout/AdministrationLayout'

import { Component as CollectiveActivityData } from './CollectiveActivityData'

vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: vi.fn() }),
}))
vi.mock('@/apiClient/api', () => ({
  api: {
    getOffererAddresses: vi.fn(),
  },
}))
vi.mock('@/commons/hooks/swr/useOffererNamesQuery', () => ({
  useOffererNamesQuery: () => ({ isLoading: false }),
}))
const mockDownloadBookableOffersFile = vi.fn()
vi.mock(
  '@/components/CollectiveOffersTable/utils/downloadBookableOffersFile',
  () => ({
    downloadBookableOffersFile: (...args: unknown[]) =>
      mockDownloadBookableOffersFile(...args),
  })
)

const routes: RouteObject[] = [
  {
    path: '/administration',
    Component: AdministrationLayout,
    children: [
      {
        path: 'donnees-activite/collectif',
        handle: { title: "Données d'activité : collectif" },
        element: (
          <>
            <CollectiveActivityData />
            <SnackBarContainer />
          </>
        ),
      },
    ],
  },
]

const renderCollectiveActivityData = () => {
  renderWithProviders(null, {
    routes,
    initialRouterEntries: ['/administration/donnees-activite/collectif'],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedAdminOfferer: defaultGetOffererResponseModel,
      },
      offerer: {
        offererNames: [defaultGetOffererResponseModel],
        currentOfferer: defaultGetOffererResponseModel,
      },
    },
  })
}

const LABEL = {
  button: {
    downloadCsv: 'Fichier CSV (.csv)',
    downloadDropdown: 'Télécharger les offres réservables',
    downloadXls: 'Microsoft Excel (.xls)',
  },
}

describe('CollectiveActivityData', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererAddresses').mockResolvedValue([])
    mockDownloadBookableOffersFile.mockResolvedValue(undefined)
  })

  it('should render the subtitle', () => {
    renderCollectiveActivityData()

    expect(
      screen.getByText('Téléchargement des offres réservables')
    ).toBeInTheDocument()
  })

  it('should render the search filters', () => {
    renderCollectiveActivityData()

    expect(screen.getByLabelText('Format')).toBeInTheDocument()
  })

  it('should render the download dropdown', () => {
    renderCollectiveActivityData()

    expect(
      screen.getByRole('button', { name: LABEL.button.downloadDropdown })
    ).toBeInTheDocument()
  })

  it('should download CSV file when selecting CSV option', async () => {
    renderCollectiveActivityData()

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.button.downloadDropdown })
    )
    await userEvent.click(
      screen.getByRole('menuitem', { name: LABEL.button.downloadCsv })
    )

    await waitFor(() => {
      expect(mockDownloadBookableOffersFile).toHaveBeenCalledWith(
        expect.objectContaining({
          offererId: defaultGetOffererResponseModel.id.toString(),
        }),
        'CSV'
      )
    })
  })

  it('should download XLS file when selecting XLS option', async () => {
    renderCollectiveActivityData()

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.button.downloadDropdown })
    )
    await userEvent.click(
      screen.getByRole('menuitem', { name: LABEL.button.downloadXls })
    )

    await waitFor(() => {
      expect(mockDownloadBookableOffersFile).toHaveBeenCalledWith(
        expect.objectContaining({
          offererId: defaultGetOffererResponseModel.id.toString(),
        }),
        'XLS'
      )
    })
  })

  it('should display an error message when download fails', async () => {
    mockDownloadBookableOffersFile.mockRejectedValueOnce(
      new Error('Download failed')
    )

    renderCollectiveActivityData()

    await userEvent.click(
      screen.getByRole('button', { name: LABEL.button.downloadDropdown })
    )
    await userEvent.click(
      screen.getByRole('menuitem', { name: LABEL.button.downloadCsv })
    )

    expect(await screen.findByText(GET_DATA_ERROR_MESSAGE)).toBeInTheDocument()
  })

  it('should reset filters when clicking reset button', async () => {
    renderCollectiveActivityData()

    await userEvent.selectOptions(screen.getByLabelText('Format'), 'Concert')

    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(screen.getByLabelText('Format')).toHaveValue('all')
  })
})
