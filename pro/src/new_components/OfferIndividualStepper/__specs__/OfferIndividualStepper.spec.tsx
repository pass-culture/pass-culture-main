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
            path={['/offre/:offerId/v3/creation/individuelle/confirmation']}
          >
            <div>Confirmation screen</div>
          </Route>
        </Switch>
      </MemoryRouter>
    </OfferIndividualContext.Provider>
  )

  const tabInformations = screen.queryByText('Informations')
  const tabStocks = screen.queryByText('Stock & Prix')
  const tabSummary = screen.queryByText('Récapitulatif')
  const tabConfirmation = screen.queryByText('Confirmation')

  return {
    ...rtlReturns,
    tabInformations,
    tabStocks,
    tabSummary,
    tabConfirmation,
  }
}

describe('test OfferIndividualStepper', () => {
  describe('in creation', () => {
    it('should render stepper breadcrumb in creation', async () => {
      await renderOfferIndividualStepper()

      expect(await screen.getByTestId('stepper')).toBeInTheDocument()
    })

    it('should render steps when no offer is given', async () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        await renderOfferIndividualStepper()

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(await screen.getByTestId('stepper')).toBeInTheDocument()

      tabStocks && (await userEvent.click(tabStocks))
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      tabSummary && (await userEvent.click(tabSummary))
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      tabConfirmation && (await userEvent.click(tabConfirmation))
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

      tabStocks && (await userEvent.click(tabStocks))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      tabSummary && (await userEvent.click(tabSummary))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      tabConfirmation && (await userEvent.click(tabConfirmation))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })

    it('should render steps when offer and stock are given', async () => {
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

      tabStocks && (await userEvent.click(tabStocks))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      tabSummary && (await userEvent.click(tabSummary))
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
      tabConfirmation && (await userEvent.click(tabConfirmation))
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
    })

    it('should render steps on Information', async () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        await renderOfferIndividualStepper(
          undefined,
          '/offre/AA/v3/creation/individuelle/informations'
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps on Stocks', async () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        await renderOfferIndividualStepper(
          undefined,
          '/offre/AA/v3/creation/individuelle/stocks'
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })

    it('should render steps on Summary', async () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        await renderOfferIndividualStepper(
          undefined,
          '/offre/AA/v3/creation/individuelle/recapitulatif'
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
    })
  })

  describe('in edition', () => {
    it('should render default breadcrumb in edition', async () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }
      await renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/individuelle/informations'
      )

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(await screen.getByTestId('bc-default')).toBeInTheDocument()
    })

    it('should render steps on Information', async () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }

      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        await renderOfferIndividualStepper(
          contextOverride,
          '/offre/AA/v3/individuelle/informations'
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps on Stocks', async () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }

      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        await renderOfferIndividualStepper(
          contextOverride,
          '/offre/AA/v3/individuelle/stocks'
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()

      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })
  })
})
