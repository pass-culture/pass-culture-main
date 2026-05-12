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
    vi.mocked(getOfferEnhancementCardsVisibility).mockReturnValue({
      shouldDisplayRecommendationCard: true,
      shouldDisplayHighlightCard: true,
      shouldDisplayHeadlineCard: true,
    })
  })

  it('should display a pending message when offer is pending for validation', () => {
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride)
    expect(
      screen.getByRole('link', {
        name: /Visualiser l’offre dans l’application/,
      })
    ).toHaveAttribute('href', `https://localhost/offre/${offer.id}`)
    expect(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    ).toHaveAttribute('href', `/offre/individuelle/creation/description`)
    expect(
      screen.getByRole('link', { name: 'Voir la liste des offres' })
    ).toHaveAttribute('href', `/offres`)
  })

  it('should display a pending message when offer is scheduled and pending for validation', () => {
    offer.publicationDate = new Date(Date.now() + 3600).toISOString()
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride)
    expect(
      screen.queryByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).not.toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    ).toHaveAttribute('href', `/offre/individuelle/creation/description`)
    expect(
      screen.getByRole('link', { name: 'Voir la liste des offres' })
    ).toHaveAttribute('href', `/offres`)
  })

  it('should display a success message when offer is accepted', () => {
    renderOffer(contextOverride)
    expect(
      screen.getByRole('link', {
        name: /Visualiser l’offre dans l’application/,
      })
    ).toHaveAttribute('href', `https://localhost/offre/${offer.id}`)
    expect(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    ).toHaveAttribute('href', `/offre/individuelle/creation/description`)
  })

  it('should redirect to offer creation first step', () => {
    renderOffer(contextOverride)

    expect(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    ).toHaveAttribute('href', `/offre/individuelle/creation/description`)
  })

  describe('enhancement cards section', () => {
    it('should not display the cards section when the WIP_OFFER_RECOMMENDATION_PRO feature flag is off', () => {
      renderOffer(contextOverride)

      expect(
        screen.queryByRole('heading', {
          name: /Allez plus loin et optimisez votre offre/,
        })
      ).not.toBeInTheDocument()
    })

    it('should display the three cards for an active event offer', async () => {
      renderOffer(contextOverride, ['WIP_OFFER_RECOMMENDATION_PRO'])

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
      renderOffer(contextOverride, ['WIP_OFFER_RECOMMENDATION_PRO'])

      expect(
        screen.queryByRole('heading', {
          name: /Allez plus loin et optimisez votre offre/,
        })
      ).not.toBeInTheDocument()
    })
  })
})
