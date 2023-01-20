import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { generatePath, MemoryRouter, Route, Switch } from 'react-router'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { configureTestStore } from 'store/testUtils'

import { OFFER_WIZARD_STEP_IDS } from '../constants'
import OfferIndividualStepper from '../OfferIndividualStepper'

const renderOfferIndividualStepper = (
  contextOverride: Partial<IOfferIndividualContext> = {},
  url = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode: OFFER_WIZARD_MODE.CREATION,
  }),
  storeOverrides = {}
) => {
  const contextValues: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    isFirstOffer: false,
    venuesMissingReimbursementPoint: {},
    ...contextOverride,
  }
  const store = configureTestStore(storeOverrides)
  const rtlReturns = render(
    <Provider store={store}>
      <OfferIndividualContext.Provider value={contextValues}>
        <MemoryRouter initialEntries={[url]}>
          <OfferIndividualStepper />
          <Switch>
            <Route
              path={[
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
                  mode: OFFER_WIZARD_MODE.CREATION,
                }),
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
                  mode: OFFER_WIZARD_MODE.EDITION,
                }),
              ]}
            >
              <div>Informations screen</div>
            </Route>
            <Route
              path={[
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.STOCKS,
                  mode: OFFER_WIZARD_MODE.CREATION,
                }),
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.STOCKS,
                  mode: OFFER_WIZARD_MODE.EDITION,
                }),
              ]}
            >
              <div>Stocks screen</div>
            </Route>
            <Route
              path={[
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.TARIFS,
                  mode: OFFER_WIZARD_MODE.CREATION,
                }),
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.TARIFS,
                  mode: OFFER_WIZARD_MODE.EDITION,
                }),
              ]}
            >
              <div>Tarifs screen</div>
            </Route>
            <Route
              path={[
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.SUMMARY,
                  mode: OFFER_WIZARD_MODE.CREATION,
                }),
                getOfferIndividualPath({
                  step: OFFER_WIZARD_STEP_IDS.SUMMARY,
                  mode: OFFER_WIZARD_MODE.EDITION,
                }),
              ]}
            >
              <div>Summary screen</div>
            </Route>
            <Route
              path={getOfferIndividualPath({
                step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
                mode: OFFER_WIZARD_MODE.CREATION,
              })}
            >
              <div>Confirmation screen</div>
            </Route>
          </Switch>
        </MemoryRouter>
      </OfferIndividualContext.Provider>
    </Provider>
  )

  const tabInformations = screen.queryByText('Détails de l’offre')
  const tabStocks = screen.queryByText('Stock & Prix')
  const tabPriceCategories = screen.queryByText('Tarifs')
  const otherNameTabStocks = screen.queryByText('Dates & Capacités')
  const tabSummary = screen.queryByText('Récapitulatif')
  const tabConfirmation = screen.queryByText('Confirmation')

  return {
    ...rtlReturns,
    tabInformations,
    tabStocks,
    tabSummary,
    tabConfirmation,
    tabPriceCategories,
    otherNameTabStocks,
  }
}

describe('test OfferIndividualStepper', () => {
  describe('in creation', () => {
    it('should render stepper breadcrumb in creation', () => {
      renderOfferIndividualStepper()

      expect(screen.getByTestId('stepper')).toBeInTheDocument()
    })

    it('should render steps when no offer is given', async () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualStepper()

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(screen.getByTestId('stepper')).toBeInTheDocument()

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
        renderOfferIndividualStepper(contextOverride)

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
        renderOfferIndividualStepper(contextOverride)

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

    it('should render steps on Information', () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualStepper(
          undefined,
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode: OFFER_WIZARD_MODE.CREATION,
            }),
            { offerId: 'AA' }
          )
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps on Stocks', () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualStepper(
          undefined,
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode: OFFER_WIZARD_MODE.CREATION,
            }),
            { offerId: 'AA' }
          )
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })

    it('should render steps on Summary', () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualStepper(
          undefined,
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            }),
            { offerId: 'AA' }
          )
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
    })

    describe('when WIP_ENABLE_MULTI_PRICE_STOCKS is active and event', () => {
      it('should render steps on tarif', () => {
        const {
          tabInformations,
          otherNameTabStocks,
          tabPriceCategories,
          tabSummary,
          tabConfirmation,
        } = renderOfferIndividualStepper(
          {
            offer: {
              id: 'AA',
              isEvent: true,
              stocks: [{ id: 'AA' } as IOfferIndividualStock],
            } as IOfferIndividual,
          },
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.TARIFS,
              mode: OFFER_WIZARD_MODE.CREATION,
            }),
            { offerId: 'AA' }
          ),
          {
            features: {
              list: [
                { isActive: true, nameKey: 'WIP_ENABLE_MULTI_PRICE_STOCKS' },
              ],
            },
          }
        )

        expect(tabInformations).toBeInTheDocument()
        expect(otherNameTabStocks).toBeInTheDocument()
        expect(tabPriceCategories).toBeInTheDocument()

        expect(tabSummary).toBeInTheDocument()
        expect(tabConfirmation).toBeInTheDocument()
        expect(screen.getByText('Tarifs screen')).toBeInTheDocument()
      })
    })
  })

  describe('in edition', () => {
    it('should render default breadcrumb in edition', () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }
      renderOfferIndividualStepper(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        )
      )

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(screen.getByTestId('bc-tab')).toBeInTheDocument()
    })

    it('should render steps on Information', () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }

      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualStepper(
          contextOverride,
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode: OFFER_WIZARD_MODE.EDITION,
            }),
            { offerId: 'AA' }
          )
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps on Stocks', () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }

      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualStepper(
          contextOverride,
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode: OFFER_WIZARD_MODE.EDITION,
            }),
            { offerId: 'AA' }
          )
        )

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()

      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })
  })
})
