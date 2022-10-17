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
  contextValue,
}: {
  storeOverride: Partial<RootState>
  contextValue: IOfferIndividualContext
}) => {
  const store = configureTestStore(storeOverride)
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
  let contextValue: IOfferIndividualContext
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
    contextValue = {
      offerId: null,
      offer: offer as IOfferIndividual,
      venueList: [],
      offererNames: [],
      categories: [],
      subCategories: [],
      reloadOffer: () => {},
    }
  })

  it('should render stock thing', async () => {
    contextValue.offer = {
      ...contextValue.offer,
      isEvent: false,
      isDigital: false,
    } as IOfferIndividual
    renderStocksScreen({ storeOverride, contextValue })
    expect(
      screen.getByText(
        'Les utilisateurs ont 30 jours pour annuler leurs réservations d’offres numériques. Dans le cas d’offres avec codes d’activation, les utilisateurs ne peuvent pas annuler leurs réservations d’offres numériques. Toute réservation est définitive et sera immédiatement validée.'
      )
    ).toBeInTheDocument()
  })
  it('should render stock event', async () => {
    contextValue.offer = {
      ...contextValue.offer,
      isEvent: true,
    } as IOfferIndividual
    renderStocksScreen({ storeOverride, contextValue })
    expect(screen.getByText('TODO Stock Event screen')).toBeInTheDocument()
  })
})
