import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import useSWR, { type SWRResponse } from 'swr'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import type {
  GetIndividualOfferWithAddressResponseModel,
  HighlightResponseModel,
  ShortHighlightResponseModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { GET_HIGHLIGHTS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferHighlightForm } from '../OfferHighlightForm'
import * as highlightUtils from '../utils'

const mockLogEvent = vi.fn()

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

function renderOfferHighlightForm({
  offerId,
  highlightRequests = [],
  onSuccess = () => {},
}: {
  offerId: number
  highlightRequests?: Array<ShortHighlightResponseModel>
  onSuccess?: () => void
}) {
  return renderWithProviders(
    <DialogBuilder defaultOpen title="test">
      <OfferHighlightForm
        offerId={offerId}
        onSuccess={onSuccess}
        highlightRequests={highlightRequests}
      />
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
    renderOfferHighlightForm({ offerId: 1 })

    await waitFor(() => {
      expect(
        screen.getByText(
          'Pré-requis pour être sélectionnée par notre équipe éditoriale :'
        )
      ).toBeInTheDocument()
    })
  })

  it('should call useSWR', async () => {
    renderOfferHighlightForm({ offerId: 1 })

    await waitFor(() => {
      expect(useSWRMock).toHaveBeenCalledWith(
        [GET_HIGHLIGHTS_QUERY_KEY],
        expect.any(Function),
        { fallbackData: [] }
      )
    })
  })

  it('should delegate to api.getHighlights', async () => {
    renderOfferHighlightForm({ offerId: 1 })

    const fetcher = useSWRMock.mock.calls[0][1]
    await fetcher!()

    expect(getHighlightsMock).toHaveBeenCalledOnce()
  })

  it('should display spinner', () => {
    useSWRMock.mockReturnValue({
      isLoading: true,
      data: undefined,
    } as SWRResponse)

    renderOfferHighlightForm({ offerId: 1 })

    expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should display checkboxes', async () => {
    renderOfferHighlightForm({ offerId: 1 })

    const checkboxes = await screen.findAllByRole('checkbox')
    expect(checkboxes).toHaveLength(mockedHighlights.length)
  })

  it('should check highlight when highlight request has already been made', async () => {
    renderOfferHighlightForm({
      offerId: 1,
      highlightRequests: [{ name: 'Highlight 1', id: 1 }],
    })

    const checkboxes = await screen.findAllByRole('checkbox')
    expect(checkboxes).toHaveLength(mockedHighlights.length)
    expect(checkboxes[0]).toBeChecked()
  })

  it('should call getDateTag with correct parameters for each highlight', async () => {
    renderOfferHighlightForm({ offerId: 1 })

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

  it('should call api.postHighlightRequestOffer and log', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderOfferHighlightForm({ offerId: 1 })

    const checkbox = await screen.findByText(mockedHighlights[0].name)
    await userEvent.click(checkbox)

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    expect(postHighlightRequestOfferMock).toHaveBeenCalledWith(1, {
      highlight_ids: [1],
    })
    expect(mockLogEvent).toBeCalledWith(
      HighlightEvents.HAS_VALIDATED_HIGHLIGHT,
      { offerId: 1, highlightIds: [1] }
    )
  })

  it('should call notify.success when new highlights list is submitted', async () => {
    renderOfferHighlightForm({ offerId: 1 })

    const checkbox = await screen.findByText(mockedHighlights[0].name)
    await userEvent.click(checkbox)

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(mockNotify.success).toHaveBeenCalledWith(
        'La sélection des temps forts a bien été prise en compte'
      )
    })
  })

  it('should notify a success when several highlights are submitted', async () => {
    renderOfferHighlightForm({
      offerId: 1,
      highlightRequests: mockedHighlights,
    })

    await userEvent.click(await screen.findByText(mockedHighlights[0].name))
    await userEvent.click(await screen.findByText(mockedHighlights[1].name))

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(mockNotify.success).toHaveBeenCalledWith(
        'Les temps forts ont été dissociés'
      )
    })
  })

  it('should not call notify.success when same highlights list is submitted', async () => {
    renderOfferHighlightForm({ offerId: 1 })

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(mockNotify.success).not.toHaveBeenCalled()
    })
  })

  it('should call notify.error', async () => {
    vi.spyOn(api, 'postHighlightRequestOffer').mockRejectedValueOnce('Error')
    renderOfferHighlightForm({ offerId: 1 })

    const checkbox = await screen.findByText(mockedHighlights[0].name)
    await userEvent.click(checkbox)

    const submitButton = screen.getByRole('button', {
      name: 'Valider la sélection',
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(mockNotify.error).toHaveBeenCalledWith(
        'Une erreur est survenue lors de la sélection des temps forts'
      )
    })
  })
})
