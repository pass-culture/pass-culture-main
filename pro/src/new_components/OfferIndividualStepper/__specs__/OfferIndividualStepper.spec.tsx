import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter, Route, Switch } from 'react-router'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'

import OfferIndividualStepper from '../OfferIndividualStepper'

const renderOfferIndividualStepper = (
  contextOverride: Partial<IOfferIndividualContext> = {},
  url = '/offre/AA/v3/creation/individuelle/informations'
) => {
  const contextValues: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    reloadOffer: () => {},
    ...contextOverride,
  }
  const rtlReturns = render(
    <OfferIndividualContext.Provider value={contextValues}>
      <MemoryRouter initialEntries={[url]}>
        <OfferIndividualStepper />
        <Switch>
          <Route
            path={[
              '/offre/:offerId/v3/creation/individuelle/informations',
              '/offre/:offerId/v3/individuelle/informations',
            ]}
          >
            <div>Informations screen</div>
          </Route>
          <Route
            path={[
              '/offre/:offerId/v3/creation/individuelle/stocks',
              '/offre/:offerId/v3/individuelle/stocks',
            ]}
          >
            <div>Stocks screen</div>
          </Route>
          <Route
            path={[
              '/offre/:offerId/v3/creation/individuelle/recapitulatif',
              '/offre/:offerId/v3/individuelle/recapitulatif',
            ]}
          >
            <div>Summary screen</div>
          </Route>
          <Route
            path={[
              '/offre/:offerId/v3/creation/individuelle/confirmation',
              '/offre/:offerId/v3/individuelle/confirmation',
            ]}
          >
            <div>Confirmation screen</div>
          </Route>
        </Switch>
      </MemoryRouter>
    </OfferIndividualContext.Provider>
  )

  const tabInformations = screen.getByText('Informations')
  const tabStocks = screen.getByText('Stock & Prix')
  const tabSummary = screen.getByText('Récapitulatif')
  const tabConfirmation = screen.getByText('Confirmation')

  return {
    ...rtlReturns,
    tabInformations,
    tabStocks,
    tabSummary,
    tabConfirmation,
  }
}

describe('test OfferIndividualStepper', () => {
  it('should render steps when no offer is given', async () => {
    const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
      await renderOfferIndividualStepper()

    expect(tabInformations).toBeInTheDocument()
    expect(tabStocks).toBeInTheDocument()
    expect(tabSummary).toBeInTheDocument()
    expect(tabConfirmation).toBeInTheDocument()

    expect(screen.getByText('Informations screen')).toBeInTheDocument()

    await userEvent.click(tabStocks)
    expect(screen.getByText('Informations screen')).toBeInTheDocument()
    await userEvent.click(tabSummary)
    expect(screen.getByText('Informations screen')).toBeInTheDocument()
    await userEvent.click(tabConfirmation)
    expect(screen.getByText('Informations screen')).toBeInTheDocument()
  })

  it('should render steps when offer without stock is given', async () => {
    const offer: Partial<IOfferIndividual> = {
      id: 'AA',
      stocks: [],
    }

    const contextOverride: Partial<IOfferIndividualContext> = {
      offer: offer as IOfferIndividual,
    }
    const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
      await renderOfferIndividualStepper(contextOverride)

    expect(tabInformations).toBeInTheDocument()
    expect(tabStocks).toBeInTheDocument()
    expect(tabSummary).toBeInTheDocument()
    expect(tabConfirmation).toBeInTheDocument()

    expect(screen.getByText('Informations screen')).toBeInTheDocument()

    await userEvent.click(tabStocks)
    expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    await userEvent.click(tabSummary)
    expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    await userEvent.click(tabConfirmation)
    expect(screen.getByText('Stocks screen')).toBeInTheDocument()
  })

  it.only('should render steps when offer and stock are given', async () => {
    const offer: Partial<IOfferIndividual> = {
      id: 'AA',
      stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
    }

    const contextOverride: Partial<IOfferIndividualContext> = {
      offer: offer as IOfferIndividual,
    }
    const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
      await renderOfferIndividualStepper(contextOverride)

    expect(tabInformations).toBeInTheDocument()
    expect(tabStocks).toBeInTheDocument()
    expect(tabSummary).toBeInTheDocument()
    expect(tabConfirmation).toBeInTheDocument()

    expect(screen.getByText('Informations screen')).toBeInTheDocument()

    await userEvent.click(tabStocks)
    expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    await userEvent.click(tabSummary)
    expect(screen.getByText('Summary screen')).toBeInTheDocument()
    await userEvent.click(tabConfirmation)
    expect(screen.getByText('Summary screen')).toBeInTheDocument()
  })
})
