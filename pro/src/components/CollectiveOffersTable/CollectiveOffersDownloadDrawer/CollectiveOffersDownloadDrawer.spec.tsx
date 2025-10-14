import { act, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { EacFormat } from '@/apiClient/adage'
import { api } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { CollectiveLocationType } from '@/apiClient/v1/models/CollectiveLocationType'
import { ALL_FORMATS } from '@/commons/core/Offers/constants'
import {
  CollectiveOfferTypeEnum,
  type CollectiveSearchFiltersParams,
} from '@/commons/core/Offers/types'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersDownloadDrawer } from './CollectiveOffersDownloadDrawer'

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

const renderCollectiveOffersDownloadDrawer = (
  {
    isDisabled = false,
    filtersProp = filters,
    defaultFiltersProp = defaultFilters,
  } = {},
  features = ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE']
) => {
  return renderWithProviders(
    <CollectiveOffersDownloadDrawer
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

  it('should render download button with drawer action', async () => {
    renderCollectiveOffersDownloadDrawer()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    expect(
      screen.getByRole('button', { name: 'Télécharger format CSV' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger format Excel' })
    ).toBeInTheDocument()
  })

  it('should be disabled when isDisabled prop is true', () => {
    renderCollectiveOffersDownloadDrawer({
      isDisabled: true,
      filtersProp: filters,
      defaultFiltersProp: defaultFilters,
    })

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    expect(downloadButton).toBeDisabled()
  })

  it('should download CSV file when CSV button is clicked', async () => {
    const mockGetCollectiveOffersCsv = vi
      .spyOn(api, 'getCollectiveOffersCsv')
      .mockResolvedValueOnce('csv,data')

    renderCollectiveOffersDownloadDrawer()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('button', {
      name: 'Télécharger format CSV',
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
      undefined,
      undefined
    )
  })

  it('should download Excel file when Excel button is clicked', async () => {
    const mockGetCollectiveOffersExcel = vi
      .spyOn(api, 'getCollectiveOffersExcel')
      .mockResolvedValueOnce(new Blob())

    renderCollectiveOffersDownloadDrawer()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const excelButton = screen.getByRole('button', {
      name: 'Télécharger format Excel',
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
      undefined,
      undefined
    )
  })

  it('should show error notification when download fails', async () => {
    vi.spyOn(api, 'getCollectiveOffersCsv').mockRejectedValueOnce(
      new Error('Download failed')
    )

    renderCollectiveOffersDownloadDrawer()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('button', {
      name: 'Télécharger format CSV',
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

    renderCollectiveOffersDownloadDrawer()

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('button', {
      name: 'Télécharger format CSV',
    })
    await userEvent.click(csvButton)

    // Wait for the state to update
    await waitFor(() => {
      expect(downloadButton).toBeDisabled()
    })

    // Resolve the download
    await act(async () => {
      resolveDownload('csv,data')
      await downloadPromise
    })

    // Button should be enabled again after download completes
    await waitFor(() => {
      expect(downloadButton).toBeEnabled()
    })
  })

  it('should include location filter when locationType is ADDRESS', async () => {
    const mockGetCollectiveOffersCsv = vi
      .spyOn(api, 'getCollectiveOffersCsv')
      .mockResolvedValueOnce('csv,data')

    const filtersWithLocation: CollectiveSearchFiltersParams = {
      ...filters,
      locationType: CollectiveLocationType.ADDRESS,
      offererAddressId: '123',
    }

    renderCollectiveOffersDownloadDrawer({
      isDisabled: false,
      filtersProp: filtersWithLocation,
      defaultFiltersProp: defaultFilters,
    })

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const csvButton = screen.getByRole('button', {
      name: 'Télécharger format CSV',
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
      CollectiveLocationType.ADDRESS,
      123
    )
  })

  it('should include location filter when locationType is SCHOOL', async () => {
    const mockGetCollectiveOffersExcel = vi
      .spyOn(api, 'getCollectiveOffersExcel')
      .mockResolvedValueOnce(new Blob())

    const filtersWithLocation: CollectiveSearchFiltersParams = {
      ...filters,
      locationType: CollectiveLocationType.SCHOOL,
    }

    renderCollectiveOffersDownloadDrawer({
      isDisabled: false,
      filtersProp: filtersWithLocation,
      defaultFiltersProp: defaultFilters,
    })

    const downloadButton = screen.getByRole('button', { name: 'Télécharger' })
    await userEvent.click(downloadButton)

    const excelButton = screen.getByRole('button', {
      name: 'Télécharger format Excel',
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
      CollectiveLocationType.SCHOOL,
      null
    )
  })
})
