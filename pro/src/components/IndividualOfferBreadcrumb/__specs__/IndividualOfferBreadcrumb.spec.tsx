import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import {
  individualOfferContextFactory,
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OFFER_WIZARD_STEP_IDS } from '../constants'
import { IndividualOfferBreadcrumb } from '../IndividualOfferBreadcrumb'

const offerId = 12
const stockId = 55

const renderIndividualOfferBreadcrumb = (
  contextOverride: Partial<IndividualOfferContextValues> = {},
  url = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode: OFFER_WIZARD_MODE.CREATION,
  }),
  storeOverrides = {}
) => {
  const contextValues = individualOfferContextFactory(contextOverride)

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferBreadcrumb />
      <Routes>
        {[OFFER_WIZARD_MODE.CREATION, OFFER_WIZARD_MODE.EDITION].map(mode => (
          <React.Fragment key={mode}>
            <Route
              path={getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
                mode,
              })}
              element={<div>Informations screen</div>}
            />

            <Route
              path={getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.STOCKS,
                mode,
              })}
              element={<div>Stocks screen</div>}
            />

            <Route
              path={getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.TARIFS,
                mode,
              })}
              element={<div>Tarifs screen</div>}
            />

            <Route
              path={getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.SUMMARY,
                mode,
              })}
              element={<div>Summary screen</div>}
            />
          </React.Fragment>
        ))}

        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Confirmation screen</div>}
        />
      </Routes>
    </IndividualOfferContext.Provider>,
    { storeOverrides, initialRouterEntries: [url] }
  )
}

describe('test IndividualOfferBreadcrumb', () => {
  describe('in creation', () => {
    it('should render stepper breadcrumb in creation', () => {
      renderIndividualOfferBreadcrumb()

      expect(screen.getByTestId('stepper')).toBeInTheDocument()
    })

    it('should render steps when no offer is given', async () => {
      renderIndividualOfferBreadcrumb({
        offer: individualOfferFactory({ isEvent: false }),
      })

      expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
      expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
      expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
      expect(screen.getByText('Confirmation')).toBeInTheDocument()

      expect(screen.getByText('Informations screen')).toBeInTheDocument()
      expect(screen.getByTestId('stepper')).toBeInTheDocument()

      await userEvent.click(screen.getByText('Stock & Prix'))
      expect(screen.getByText('Stocks screen')).toBeInTheDocument()
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(screen.getByText('Summary screen')).toBeInTheDocument()
    })

    it('should render steps when offer without stock is given', async () => {
      const offer = individualOfferFactory({
        stocks: [],
        isEvent: false,
      })

      renderIndividualOfferBreadcrumb({ offer })

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
      const offer = individualOfferFactory({
        isEvent: false,
      })

      renderIndividualOfferBreadcrumb({ offer })

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
      renderIndividualOfferBreadcrumb(
        { offer: individualOfferFactory({ isEvent: false }) },
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        { offer: individualOfferFactory({ isEvent: false }) },
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        { offer: individualOfferFactory({ isEvent: false }) },
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        {
          offer: {
            ...individualOfferFactory(),
            isEvent: true,
          },
        },
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        {
          offer: {
            ...individualOfferFactory(),
            isEvent: false,
          },
        },
        generatePath(
          getIndividualOfferPath({
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
      const offer = individualOfferFactory({
        id: offerId,
        stocks: [individualStockFactory({ id: stockId })],
      })

      renderIndividualOfferBreadcrumb(
        { offer },
        generatePath(
          getIndividualOfferPath({
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
      const offer = individualOfferFactory({
        id: offerId,
        stocks: [individualStockFactory({ id: stockId })],
        isEvent: false,
      })

      renderIndividualOfferBreadcrumb(
        { offer },
        generatePath(
          getIndividualOfferPath({
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
      const offer = individualOfferFactory({
        id: offerId,
        stocks: [individualStockFactory({ id: stockId })],
        isEvent: false,
      })

      renderIndividualOfferBreadcrumb(
        { offer },
        generatePath(
          getIndividualOfferPath({
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
