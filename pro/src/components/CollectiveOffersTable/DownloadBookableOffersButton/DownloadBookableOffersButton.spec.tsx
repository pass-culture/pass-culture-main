import { act, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { EacFormat } from '@/apiClient/adage'
import { api } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { ALL_FORMATS } from '@/commons/core/Offers/constants'
import {
  CollectiveOfferTypeEnum,
  type CollectiveSearchFiltersParams,
} from '@/commons/core/Offers/types'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { DownloadBookableOffersButton } from './DownloadBookableOffersButton'

vi.mock('@/commons/utils/downloadFile', () => ({ downloadFile: vi.fn() }))

const mockNotifyError = vi.fn()
const mockNotifySuccess = vi.fn()

vi.mock('@/commons/hooks/useNotification', () => ({
  useNotification: () => ({
    error: mockNotifyError,
    success: mockNotifySuccess,
  }),
}))

const defaultFilters: CollectiveSearchFiltersParams = {
  nameOrIsbn: '',
  offererId: '',
  venueId: '',
  status: [],
  periodBeginningDate: '',
  periodEndingDate: '',
  collectiveOfferType: CollectiveOfferTypeEnum.ALL,
  format: ALL_FORMATS,
}

const filters: CollectiveSearchFiltersParams = {
  nameOrIsbn: 'test offer',
  offererId: '1',
  venueId: '2',
  status: [CollectiveOfferDisplayedStatus.PUBLISHED],
  periodBeginningDate: '2023-01-01',
  periodEndingDate: '2023-12-31',
  collectiveOfferType: CollectiveOfferTypeEnum.OFFER,
  format: EacFormat.CONCERT,
}

const renderDownloadButton = (
  {
    isDisabled = false,
    filtersProp = filters,
    defaultFiltersProp = defaultFilters,
  } = {},
  features = ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE']
) => {
  return renderWithProviders(
    <DownloadBookableOffersButton
      isDisabled={isDisabled}
      filters={filtersProp}
      defaultFilters={defaultFiltersProp}
    />,
    { features }
  )
}

describe('DownloadBookableOffersButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render download button with dropdown options', async () => {
    renderDownloadButton()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    expect(downloadButton).toBeInTheDocument()
    expect(downloadButton).toBeEnabled()

    await userEvent.click(downloadButton)

    expect(
      screen.getByRole('menuitem', { name: 'Microsoft Excel (.xls)' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('menuitem', { name: 'Fichier CSV (.csv)' })
    ).toBeInTheDocument()
  })

  it('should not render download button when WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE is not active', () => {
    renderDownloadButton(
      {
        isDisabled: false,
        filtersProp: filters,
        defaultFiltersProp: defaultFilters,
      },
      []
    )

    const downloadButton = screen.queryByRole('button', { name: 'Télécharger' })
    expect(downloadButton).not.toBeInTheDocument()
  })

  it('should be disabled when isDisabled prop is true', () => {
    renderDownloadButton({
      isDisabled: true,
      filtersProp: filters,
      defaultFiltersProp: defaultFilters,
    })

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    expect(downloadButton).toBeDisabled()
  })

  it('should download CSV file when CSV option is clicked', async () => {
    const mockGetCollectiveOffersCsv = vi
      .spyOn(api, 'getCollectiveOffersCsv')
      .mockResolvedValueOnce('csv,data')

    renderDownloadButton()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('menuitem', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(csvButton)

    expect(mockGetCollectiveOffersCsv).toHaveBeenCalledWith(
      'test offer',
      '1',
      ['PUBLISHED'],
      '2',
      undefined,
      '2023-01-01',
      '2023-12-31',
      'offer',
      'Concert',
      null,
      null
    )
  })

  it('should download Excel file when Excel option is clicked', async () => {
    const mockGetCollectiveOffersExcel = vi
      .spyOn(api, 'getCollectiveOffersExcel')
      .mockResolvedValueOnce(new Blob())

    renderDownloadButton()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const excelButton = screen.getByRole('menuitem', {
      name: 'Microsoft Excel (.xls)',
    })
    await userEvent.click(excelButton)

    expect(mockGetCollectiveOffersExcel).toHaveBeenCalledWith(
      'test offer',
      '1',
      ['PUBLISHED'],
      '2',
      undefined,
      '2023-01-01',
      '2023-12-31',
      'offer',
      'Concert',
      null,
      null
    )
  })

  it('should show error notification when download fails', async () => {
    vi.spyOn(api, 'getCollectiveOffersCsv').mockRejectedValueOnce(
      new Error('Download failed')
    )

    renderDownloadButton()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('menuitem', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(csvButton)

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Nous avons rencontré un problème lors de la récupération des données.'
    )
  })

  it('should disable button while downloading', async () => {
    let resolveDownload: (value: string) => void
    const downloadPromise = new Promise<string>((resolve) => {
      resolveDownload = resolve
    })

    vi.spyOn(api, 'getCollectiveOffersCsv').mockReturnValueOnce(
      downloadPromise as any
    )

    renderDownloadButton()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('menuitem', {
      name: 'Fichier CSV (.csv)',
    })
    await userEvent.click(csvButton)

    // Wait for the state to update
    await waitFor(() => {
      expect(downloadButton).toBeDisabled()
    })

    // Resolve the download
    await act(async () => {
      resolveDownload!('csv,data')
      await downloadPromise
    })

    // Button should be enabled again after download completes
    await waitFor(() => {
      expect(downloadButton).toBeEnabled()
    })
  })
})
