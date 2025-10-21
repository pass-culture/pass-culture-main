import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import useSWR, { type SWRResponse } from 'swr'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import type {
  GetIndividualOfferWithAddressResponseModel,
  HighlightResponseModel,
} from '@/apiClient/v1'
import { GET_HIGHLIGHTS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferHighlightForm } from '../OfferHighlightForm'
import * as highlightUtils from '../utils'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))

vi.mock('../utils', () => ({
  getDateTag: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    getHighlights: vi.fn(),
    postHighlightRequestOffer: vi.fn(),
  },
}))

const mockNotify = {
  success: vi.fn(),
  error: vi.fn(),
}
vi.mock('@/commons/hooks/useNotification', () => ({
  useNotification: () => mockNotify,
}))

const mockedHighlights: HighlightResponseModel[] = [
  {
    id: 1,
    name: 'Highlight 1',
    description: 'Description 1',
    availabilityTimespan: ['2025-01-01', '2025-01-15'],
    highlightTimespan: ['2025-01-10', '2025-01-31'],
    mediationUrl: '',
  },
  {
    id: 2,
    name: 'Highlight 2',
    description: 'Description 2',
    availabilityTimespan: ['2025-02-01', '2025-02-15'],
    highlightTimespan: ['2025-02-10', '2025-02-28'],
    mediationUrl: '',
  },
]

function renderOfferHighlightForm(props: {
  offerId: number
  onSuccess?: () => void
}) {
  const { onSuccess = () => {} } = props
  return renderWithProviders(
    <DialogBuilder defaultOpen title="test">
      <OfferHighlightForm {...props} onSuccess={onSuccess} />
    </DialogBuilder>
  )
}

describe('OfferHighlightForm', () => {
  const useSWRMock = vi.mocked(useSWR)
  const getHighlightsMock = vi.mocked(api.getHighlights)
  const postHighlightRequestOfferMock = vi.mocked(api.postHighlightRequestOffer)
  const getDateTagMock = vi.mocked(highlightUtils.getDateTag)

  beforeEach(() => {
    vi.clearAllMocks()
    vi.resetAllMocks()
    getHighlightsMock.mockResolvedValue(mockedHighlights)
    postHighlightRequestOfferMock.mockResolvedValue(
      {} as GetIndividualOfferWithAddressResponseModel
    )

    useSWRMock.mockReturnValue({
      data: mockedHighlights,
      isLoading: false,
    } as SWRResponse)

    getDateTagMock.mockReturnValue('date-tag')
  })

  it('should display the info callout', async () => {
    // When
    renderOfferHighlightForm({ offerId: 1 })

    // Then
    await waitFor(() => {
      expect(
        screen.getByText(
          'Pré-requis pour être sélectionnée par notre équipe éditoriale :'
        )
      ).toBeInTheDocument()
    })
  })

  it('should call useSWR', async () => {
    // When
    renderOfferHighlightForm({ offerId: 1 })

    // Then
    await waitFor(() => {
      expect(useSWRMock).toHaveBeenCalledWith(
        [GET_HIGHLIGHTS_QUERY_KEY],
        expect.any(Function),
        { fallbackData: [] }
      )
    })
  })

  it('should delegate to api.getHighlights', async () => {
    // Given
    renderOfferHighlightForm({ offerId: 1 })

    // When
    const fetcher = useSWRMock.mock.calls[0][1]
    await fetcher!()

    // Then
    expect(getHighlightsMock).toHaveBeenCalledOnce()
  })

  it('should display spinner', () => {
    // Given
    useSWRMock.mockReturnValue({
      isLoading: true,
      data: undefined,
    } as SWRResponse)

    // When
    renderOfferHighlightForm({ offerId: 1 })

    // Then
    expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should display checkboxes', async () => {
    // When
    renderOfferHighlightForm({ offerId: 1 })

    // Then
    const checkboxes = await screen.findAllByRole('checkbox')
    expect(checkboxes).toHaveLength(mockedHighlights.length)
  })

  it('should call getDateTag with correct parameters for each highlight', async () => {
    // When
    renderOfferHighlightForm({ offerId: 1 })

    // Then
    await waitFor(() => {
      expect(getDateTagMock).toHaveBeenNthCalledWith(
        1,
        '2025-01-10',
        '2025-01-31'
      )
      expect(getDateTagMock).toHaveBeenNthCalledWith(
        2,
        '2025-02-10',
        '2025-02-28'
      )
    })
  })

  it('should call api.postHighlightRequestOffer', async () => {
    // Given
    renderOfferHighlightForm({ offerId: 1 })

    // When
    const checkbox = await screen.findByText(mockedHighlights[0].name)
    await userEvent.click(checkbox)

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    // Then
    expect(postHighlightRequestOfferMock).toHaveBeenCalledWith(1, {
      highlight_ids: [1],
    })
  })

  it('should call notify.success when new highlights list is submitted', async () => {
    // Given
    renderOfferHighlightForm({ offerId: 1 })

    // When
    const checkbox = await screen.findByText(mockedHighlights[0].name)
    await userEvent.click(checkbox)

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    // Then
    await waitFor(() => {
      expect(mockNotify.success).toHaveBeenCalledWith(
        'Le temps fort a bien été relié à votre offre'
      )
    })
  })

  it('should not call notify.success when same highlights list is submitted', async () => {
    // Given
    renderOfferHighlightForm({ offerId: 1 })

    // When
    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    // Then
    await waitFor(() => {
      expect(mockNotify.success).not.toHaveBeenCalled()
    })
  })

  it('should call notify.error', async () => {
    // Given
    vi.spyOn(api, 'postHighlightRequestOffer').mockRejectedValueOnce('Error')
    renderOfferHighlightForm({ offerId: 1 })

    // When
    const checkbox = await screen.findByText(mockedHighlights[0].name)
    await userEvent.click(checkbox)

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    // Then
    await waitFor(() => {
      expect(mockNotify.error).toHaveBeenCalledWith(
        'Une erreur est survenue lors de la sélection des temps forts'
      )
    })
  })
})
