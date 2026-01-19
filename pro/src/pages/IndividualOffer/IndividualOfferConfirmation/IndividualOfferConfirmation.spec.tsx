import { screen } from '@testing-library/react'
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
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
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
      </Routes>
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
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
  })

  it('should display a pending message when offer is pending for validation', () => {
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride)
    expect(screen.getByText('Offre en cours de validation')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
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
    expect(screen.getByText('Offre en cours de validation')).toBeInTheDocument()
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
    expect(screen.getByText('Offre créée avec succès !')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
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
})
