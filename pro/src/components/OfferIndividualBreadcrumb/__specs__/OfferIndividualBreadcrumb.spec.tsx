import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

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

const offerId = 12

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

  renderWithProviders(
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
}

describe('test OfferIndividualBreadcrumb', () => {
  describe('in creation', () => {
    it('should render stepper breadcrumb in creation', () => {
      renderOfferIndividualBreadcrumb()

      expect(screen.getByTestId('stepper')).toBeInTheDocument()
    })

    it('should render steps when no offer is given', async () => {
      renderOfferIndividualBreadcrumb()

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(screen.getByTestId('stepper')).toBeInTheDocument()

      await userEvent.click(screen.getByText('Stock & Prix'))
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Confirmation'))
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps when offer without stock is given', async () => {
      const offer: Partial<IOfferIndividual> = individualOfferFactory({
        stocks: [],
        isEvent: false,
      })

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }
      renderOfferIndividualBreadcrumb(contextOverride)

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()

      await userEvent.click(screen.getByText('Stock & Prix'))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Confirmation'))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })

    it('should render steps when offer and stock are given', async () => {
      const offer: Partial<IOfferIndividual> = individualOfferFactory({
        isEvent: false,
      })

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }
      renderOfferIndividualBreadcrumb(contextOverride)

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()

      await userEvent.click(screen.getByText('Stock & Prix'))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Confirmation'))
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
    })

    it('should render steps on Information', () => {
      renderOfferIndividualBreadcrumb(
        undefined,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps on Stocks', () => {
      renderOfferIndividualBreadcrumb(
        undefined,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })

    it('should render steps on Summary', () => {
      renderOfferIndividualBreadcrumb(
        undefined,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
    })

    it('should render steps on tarif', () => {
      renderOfferIndividualBreadcrumb(
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
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Dates & Capacités')).toBeInTheDocument()
      expect(screen.queryByText('Stock & Prix')).not.toBeInTheDocument()
      expect(screen.getByText('Tarifs')).toBeInTheDocument()

      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(screen.getByText('Tarifs screen')).toBeInTheDocument()
    })

    it('should not render tarif step when offer is not an event', () => {
      renderOfferIndividualBreadcrumb(
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
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.queryByText('Dates & Capacités')).not.toBeInTheDocument()
      expect(screen.queryByText('Tarifs')).not.toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })
  })

  describe('in edition', () => {
    it('should render default breadcrumb in edition', () => {
      const offer: Partial<IOfferIndividual> = {
        nonHumanizedId: offerId,
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
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(screen.getByTestId('bc-tab')).toBeInTheDocument()
    })

    it('should render steps on Information', () => {
      const offer: Partial<IOfferIndividual> = {
        nonHumanizedId: offerId,
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
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.queryByText('Récapitulatif')).not.toBeInTheDocument()
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
    })

    it('should render steps on Stocks', () => {
      const offer: Partial<IOfferIndividual> = {
        nonHumanizedId: offerId,
        stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
      }

      const contextOverride: Partial<IOfferIndividualContext> = {
        offer: offer as IOfferIndividual,
      }

      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: offerId }
        )
      )

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.queryByText('Récapitulatif')).not.toBeInTheDocument()
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()

      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
    })
  })
})
