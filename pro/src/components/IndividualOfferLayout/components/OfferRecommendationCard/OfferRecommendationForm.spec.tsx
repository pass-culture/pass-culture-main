import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, vi } from 'vitest'

import { apiNew } from '@/apiClient/api'
import type { ProAdviceModel } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferRecommendationForm } from './OfferRecommendationForm'

const mockLogEvent = vi.fn()

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    createOfferProAdvice: vi.fn(),
    updateOfferProAdvice: vi.fn(),
    deleteOfferProAdvice: vi.fn(),
  },
}))

const snackBarError = vi.fn()
const snackBarSuccess = vi.fn()

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => ({
    success: snackBarSuccess,
    error: snackBarError,
  }),
}))

function renderOfferRecommendationForm({
  offerId,
  proAdvice = null,
  onClose = () => {},
}: {
  offerId: number
  proAdvice?: ProAdviceModel | null
  onClose?: () => void
}) {
  return renderWithProviders(
    <DialogBuilder defaultOpen title="test">
      <OfferRecommendationForm
        offerId={offerId}
        onClose={onClose}
        proAdvice={proAdvice}
      />
    </DialogBuilder>,
    {
      storeOverrides: {
        user: {
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
      },
    }
  )
}

describe('OfferRecommendationForm', () => {
  it('should display the subtitle', () => {
    renderOfferRecommendationForm({ offerId: 1 })
    expect(
      screen.getByText(
        /Les jeunes sont sensibles aux recommandations de professionnels/i
      )
    ).toBeInTheDocument()
  })

  it('should call createOfferProAdvice when submitting a new recommendation', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    const createOfferProAdviceMock = vi.mocked(apiNew.createOfferProAdvice)
    createOfferProAdviceMock.mockResolvedValueOnce({
      proAdvice: { content: 'test', author: 'test', updatedAt: '' },
    } as any)

    renderOfferRecommendationForm({ offerId: 1 })

    await userEvent.type(
      screen.getByLabelText(/Recommandation/i),
      'Super offre'
    )
    await userEvent.type(screen.getByLabelText(/Recommandée par :/i), 'Jean-Mi')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer la recommandation' })
    )

    expect(createOfferProAdviceMock).toHaveBeenCalledWith({
      path: { offer_id: 1 },
      body: { content: 'Super offre', author: 'Jean-Mi' },
    })
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre recommandation a bien été ajoutée'
    )
    expect(mockLogEvent).toBeCalledWith(
      EngagementEvents.HAS_MADE_RECOMMENDATION,
      { offerId: 1, venueId: 2, action: 'validated' }
    )
  })

  it('should call updateOfferProAdvice when updating an existing recommendation', async () => {
    const updateOfferProAdviceMock = vi.mocked(apiNew.updateOfferProAdvice)
    updateOfferProAdviceMock.mockResolvedValueOnce({
      proAdvice: { content: 'new content', author: 'Jean-Mi', updatedAt: '' },
    } as any)

    renderOfferRecommendationForm({
      offerId: 1,
      proAdvice: { content: 'old content', author: 'Jean-Mi', updatedAt: '' },
    })

    await userEvent.clear(screen.getByLabelText(/Recommandation/i))
    await userEvent.type(
      screen.getByLabelText(/Recommandation/i),
      'Nouveau contenu'
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer la recommandation' })
    )

    expect(updateOfferProAdviceMock).toHaveBeenCalledWith({
      path: { offer_id: 1 },
      body: { content: 'Nouveau contenu', author: 'Jean-Mi' },
    })
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre recommandation a bien été ajoutée'
    )
  })

  it('should call deleteOfferProAdvice when clicking delete', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    const deleteOfferProAdviceMock = vi.mocked(apiNew.deleteOfferProAdvice)
    deleteOfferProAdviceMock.mockResolvedValueOnce({} as any)

    renderOfferRecommendationForm({
      offerId: 1,
      proAdvice: { content: 'content', author: 'author', updatedAt: '' },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer la recommandation' })
    )

    expect(deleteOfferProAdviceMock).toHaveBeenCalledWith({
      path: { offer_id: 1 },
    })
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre recommandation a bien été supprimée'
    )
    expect(mockLogEvent).toBeCalledWith(
      EngagementEvents.HAS_MADE_RECOMMENDATION,
      { offerId: 1, venueId: 2, action: 'deleted' }
    )
  })

  it('should show error message if content is empty', async () => {
    renderOfferRecommendationForm({ offerId: 1 })

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer la recommandation' })
    )

    await waitFor(() => {
      expect(
        screen.getByText('La recommandation est obligatoire')
      ).toBeInTheDocument()
    })
  })
})
