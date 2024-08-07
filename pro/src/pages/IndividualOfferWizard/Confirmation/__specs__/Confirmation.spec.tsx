import { screen } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { Notification } from 'components/Notification/Notification'
import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import {
  getOfferVenueFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Confirmation } from '../Confirmation'

window.open = vi.fn()

vi.mock('utils/config', async () => {
  return {
    ...(await vi.importActual('utils/config')),
    WEBAPP_URL: 'https://localhost',
  }
})

const renderOffer = (
  contextOverride: Partial<IndividualOfferContextValues>
) => {
  const contextValue = individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path="/confirmation"
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <Confirmation />
            </IndividualOfferContext.Provider>
          }
        />
      </Routes>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/confirmation'],
    }
  )
}

describe('Confirmation', () => {
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
          allowedOnAdage: true,
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
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation?structure=${offererId}&lieu=${venueId}`
    )
    expect(
      screen.getByText('Voir la liste des offres', { selector: 'a' })
    ).toHaveAttribute('href', `/offres`)
  })

  it('should display a success message when offer is accepted', () => {
    renderOffer(contextOverride)
    expect(screen.getByText('Offre publiée !')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `https://localhost/offre/${offer.id}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation?structure=${offererId}&lieu=${venueId}`
    )
  })
})
