import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import Notification from 'components/Notification/Notification'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual } from 'core/Offers/types'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import Confirmation from '../Confirmation'

jest.mock('utils/config', () => {
  return {
    WEBAPP_URL: 'http://localhost',
  }
})

const renderOffer = (
  contextOverride: Partial<IOfferIndividualContext>,
  storeOverride?: Partial<RootState>
) => {
  const contextValue: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    ...contextOverride,
  }
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    ...storeOverride,
  })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/confirmation']}>
        <Route path="/confirmation">
          <OfferIndividualContext.Provider value={contextValue}>
            <Confirmation />
          </OfferIndividualContext.Provider>
        </Route>
      </MemoryRouter>
      <Notification />
    </Provider>
  )
}

describe('Summary', () => {
  let store: any
  let contextOverride: Partial<IOfferIndividualContext>
  let offer: IOfferIndividual
  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          publicName: 'John Do',
          isAdmin: false,
          email: 'email@example.com',
        },
      },
    }
    offer = {
      nonHumanizedId: 12,
      venueId: 'VID physical',
      venue: {
        offerer: {
          id: 'OFID',
          name: 'Offerer name',
        },
      },
      status: OfferStatus.ACTIVE,
    } as IOfferIndividual
    contextOverride = {
      offer: offer,
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })
  it('should display a pending message when offer is pending for validation', () => {
    offer.status = OfferStatus.PENDING
    renderOffer(contextOverride, store)
    expect(screen.getByText('Offre en cours de validation')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `http://localhost/offre/${offer.nonHumanizedId}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation/individuel?structure=OFID&lieu=VID physical`
    )
    expect(
      screen.getByText('Voir la liste des offres', { selector: 'a' })
    ).toHaveAttribute('href', `/offres`)
  })
  it('should display a success message when offer is accepted', () => {
    renderOffer(contextOverride, store)
    expect(screen.getByText('Offre publiée !')).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `http://localhost/offre/${offer.nonHumanizedId}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation/individuel?structure=OFID&lieu=VID physical`
    )
  })
})
