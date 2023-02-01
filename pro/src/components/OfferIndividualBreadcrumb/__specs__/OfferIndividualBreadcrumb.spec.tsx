import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath } from 'react-router'
import { Route, Routes } from 'react-router-dom-v5-compat'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OFFER_WIZARD_STEP_IDS } from '../constants'
import OfferIndividualBreadcrumb from '../OfferIndividualBreadcrumb'

const renderOfferIndividualBreadcrumb = (
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
    showVenuePopin: {},
    ...contextOverride,
  }

  const rtlReturns = renderWithProviders(
    <OfferIndividualContext.Provider value={contextValues}>
      <OfferIndividualBreadcrumb />
      <Routes>
        {[OFFER_WIZARD_MODE.CREATION, OFFER_WIZARD_MODE.EDITION].map(mode => (
          <React.Fragment key={mode}>
            <Route
              path={getOfferIndividualPath({
                step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
                mode,
              })}
              element={<div>Informations screen</div>}
            />

            <Route
              path={getOfferIndividualPath({
                step: OFFER_WIZARD_STEP_IDS.STOCKS,
                mode,
              })}
              element={<div>Stocks screen</div>}
            />

            <Route
              path={getOfferIndividualPath({
                step: OFFER_WIZARD_STEP_IDS.TARIFS,
                mode,
              })}
              element={<div>Tarifs screen</div>}
            />

            <Route
              path={getOfferIndividualPath({
                step: OFFER_WIZARD_STEP_IDS.SUMMARY,
                mode,
              })}
              element={<div>Summary screen</div>}
            />
          </React.Fragment>
        ))}

        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Confirmation screen</div>}
        />
      </Routes>
    </OfferIndividualContext.Provider>,
    { storeOverrides, initialRouterEntries: [url] }
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

describe('test OfferIndividualBreadcrumb', () => {
  describe('in creation', () => {
    it('should render stepper breadcrumb in creation', () => {
      renderOfferIndividualBreadcrumb()

      expect(screen.getByTestId('stepper')).toBeInTheDocument()
    })

    it('should render steps when no offer is given', async () => {
      const { tabInformations, tabStocks, tabSummary, tabConfirmation } =
        renderOfferIndividualBreadcrumb()

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
        renderOfferIndividualBreadcrumb(contextOverride)

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
        renderOfferIndividualBreadcrumb(contextOverride)

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
        renderOfferIndividualBreadcrumb(
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
        renderOfferIndividualBreadcrumb(
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
        renderOfferIndividualBreadcrumb(
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
        } = renderOfferIndividualBreadcrumb(
          {
            offer: {
              ...individualOfferFactory(),
              isEvent: true,
            },
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

      it('should not render tarif step when offer is not an event', () => {
        const {
          tabInformations,
          tabStocks,
          otherNameTabStocks,
          tabPriceCategories,
          tabSummary,
          tabConfirmation,
        } = renderOfferIndividualBreadcrumb(
          {
            offer: {
              ...individualOfferFactory(),
              isEvent: false,
            },
          },
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
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
        expect(tabStocks).toBeInTheDocument()
        expect(otherNameTabStocks).not.toBeInTheDocument()
        expect(tabPriceCategories).not.toBeInTheDocument()
        expect(tabSummary).toBeInTheDocument()
        expect(tabConfirmation).toBeInTheDocument()
        expect(screen.getByText('Stocks screen')).toBeInTheDocument()
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
      renderOfferIndividualBreadcrumb(
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
        renderOfferIndividualBreadcrumb(
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
        renderOfferIndividualBreadcrumb(
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
