import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { getOfferEnhancementCardsVisibility } from '@/commons/core/Offers/utils/getOfferEnhancementCardsVisibility'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { IndividualOfferConfirmation } from './IndividualOfferConfirmation'

window.open = vi.fn()

vi.mock('qrcode.react', () => ({
  QRCodeSVG: vi.fn(({ value }: { value: string }) => (
    <div data-testid="qr-code" data-value={value} />
  )),
}))

vi.mock('@/commons/utils/config', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/config')),
    WEBAPP_URL: 'https://localhost',
  }
})

vi.mock(
  '@/commons/core/Offers/utils/getOfferEnhancementCardsVisibility',
  () => ({
    getOfferEnhancementCardsVisibility: vi.fn(),
  })
)

const renderOffer = (
  contextOverride: Partial<IndividualOfferContextValues>,
  features?: string[]
) => {
  const contextValue = individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path="/confirmation"
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <IndividualOfferConfirmation />
            </IndividualOfferContext.Provider>
          }
        />
        <Route
          path="/offre/individuelle/:offerId/recapitulatif/description"
          element={<div>Offer summary page</div>}
        />
      </Routes>
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
        },
      },
      initialRouterEntries: ['/confirmation'],
      features,
    }
  )
}

const waitForRecommendationCardFetch = async () => {
  await waitFor(() => {
    expect(api.getOfferProAdvice).toHaveBeenCalled()
  })
}

describe('IndividualOfferConfirmation', () => {
  let contextOverride: Partial<IndividualOfferContextValues>
  let offer: GetIndividualOfferWithAddressResponseModel
  const venueId = 45
  const offererId = 51

  beforeEach(() => {
    offer = getIndividualOfferFactory({
      venue: getOfferVenueFactory({
        id: venueId,
        managingOfferer: {
          id: offererId,
          name: 'Offerer name',
        },
      }),
      status: OfferStatus.ACTIVE,
    })
    contextOverride = {
      offer: offer,
    }
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferWithAddressResponseModel
    )
    vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({
      proAdvice: null,
    })
    vi.mocked(getOfferEnhancementCardsVisibility).mockReturnValue({
      shouldDisplayRecommendationCard: true,
      shouldDisplayHighlightCard: true,
      shouldDisplayHeadlineCard: true,
    })
  })

  it('should display a pending message when offer is pending for validation', async () => {
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride)
    await waitForRecommendationCardFetch()

    expect(
      screen.getByRole('heading', { name: /Offre en cours de validation/ })
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Cette vérification pourra prendre jusqu’à 72h/)
    ).toBeInTheDocument()
  })

  it('should display a success message when offer is accepted', async () => {
    renderOffer(contextOverride)
    await waitForRecommendationCardFetch()

    expect(
      screen.getByRole('heading', {
        name: /Votre offre a été publiée avec succès/,
      })
    ).toBeInTheDocument()
  })

  describe('preview section', () => {
    it('should show the QR code block for an active offer', async () => {
      renderOffer(contextOverride)
      await waitForRecommendationCardFetch()

      expect(screen.getByTestId('qr-code')).toBeInTheDocument()
      expect(
        screen.getByText('Visualisez votre offre sur l’application')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Scannez le QR code ou cliquez ci-dessous')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Nouvelle fenêtreVisualiser sur le web',
        })
      ).toBeInTheDocument()
    })

    it('should hide the QR code block when the offer is scheduled in the future', async () => {
      offer.publicationDate = new Date(Date.now() + 3600 * 1000).toISOString()
      renderOffer(contextOverride)
      await waitForRecommendationCardFetch()

      expect(screen.queryByTestId('qr-code')).not.toBeInTheDocument()
      expect(
        screen.queryByText('Visualisez votre offre sur l’application')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Scannez le QR code ou cliquez ci-dessous')
      ).not.toBeInTheDocument()
    })

    it('should encode the offer URL with UTM params in the QR code', async () => {
      renderOffer(contextOverride)
      await waitForRecommendationCardFetch()

      expect(screen.getByTestId('qr-code')).toHaveAttribute(
        'data-value',
        `https://localhost/offre/${offer.id}?utm_source=pro&utm_medium=qrcode&utm_gen=product&utm_campaign=proOfferPreview`
      )
    })

    it('should display the preview action links', async () => {
      renderOffer(contextOverride)
      await waitForRecommendationCardFetch()

      expect(
        screen.getByRole('link', { name: 'Créer une nouvelle offre' })
      ).toHaveAttribute('href', '/offre/individuelle/creation/description')
      expect(
        screen.getByRole('link', { name: 'Accéder à la liste des offres' })
      ).toHaveAttribute('href', '/offres')
    })
  })

  describe('enhancement cards section', () => {
    it('should display the three cards for an active event offer', async () => {
      renderOffer(contextOverride)

      expect(
        screen.getByRole('heading', {
          name: /Allez plus loin et optimisez votre offre/,
        })
      ).toBeInTheDocument()
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: 'Ajouter une recommandation' })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('button', { name: 'Relier l’offre à un temps fort' })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('button', { name: 'Mettre l’offre à la une' })
        ).toBeInTheDocument()
      })
    })

    it('should not display the cards section when there is no card to display', () => {
      vi.mocked(getOfferEnhancementCardsVisibility).mockReturnValue({
        shouldDisplayRecommendationCard: false,
        shouldDisplayHighlightCard: false,
        shouldDisplayHeadlineCard: false,
      })
      renderOffer(contextOverride)

      expect(
        screen.queryByRole('heading', {
          name: /Allez plus loin et optimisez votre offre/,
        })
      ).not.toBeInTheDocument()
    })
  })
})
