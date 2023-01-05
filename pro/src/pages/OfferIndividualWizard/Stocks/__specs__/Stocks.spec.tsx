import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import Stocks from '../Stocks'

const renderStocksScreen = ({
  storeOverride = {},
  contextOverride,
}: {
  storeOverride: Partial<RootState>
  contextOverride: Partial<IOfferIndividualContext>
}) => {
  const store = configureTestStore(storeOverride)
  const contextValue: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    shouldTrack: true,
    setShouldTrack: () => {},
    setVenueId: () => {},
    isFirstOffer: false,
    ...contextOverride,
  }
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/creation/stocks']}>
        <OfferIndividualContext.Provider value={contextValue}>
          <Stocks />
        </OfferIndividualContext.Provider>
      </MemoryRouter>
    </Provider>
  )
}

describe('screens:Stocks', () => {
  let storeOverride: Partial<RootState>
  let contextOverride: Partial<IOfferIndividualContext>
  let offer: Partial<IOfferIndividual>

  beforeEach(() => {
    offer = {
      id: 'OFFER_ID',
      venue: {
        departmentCode: '75',
      } as IOfferIndividualVenue,
      stocks: [],
    }
    storeOverride = {}
    contextOverride = {
      offerId: 'OFFER_ID',
      offer: offer as IOfferIndividual,
    }
  })

  it('should render stock thing', async () => {
    contextOverride.offer = {
      ...contextOverride.offer,
      isEvent: false,
      isDigital: false,
    } as IOfferIndividual
    renderStocksScreen({ storeOverride, contextOverride })
    expect(
      screen.getByText(
        'Les bénéficiaires ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()
  })
  it('should render stock event', async () => {
    contextOverride.offer = {
      ...contextOverride.offer,
      isEvent: true,
    } as IOfferIndividual
    renderStocksScreen({ storeOverride, contextOverride })
    expect(
      screen.getByText(
        'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’événement. Vous pouvez annuler un événement en supprimant la ligne de stock associée. Cette action est irréversible.'
      )
    ).toBeInTheDocument()
  })
})
