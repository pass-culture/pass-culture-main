import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StockSection, { StockSectionProps } from '../StockSection'

const renderStockSection = (
  props: StockSectionProps,
  url: string = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.EDITION,
  })
) =>
  renderWithProviders(
    <Routes>
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.EDITION,
        })}
        element={<StockSection {...props} />}
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<StockSection {...props} />}
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>Offer creation: page stocks</div>}
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
        })}
        element={<div>Offer edition: page stocks</div>}
      />
    </Routes>,
    { initialRouterEntries: [url] }
  )

describe('Summary stock section', () => {
  describe('for general case', () => {
    it('should render sold out warning', () => {
      const props = {
        offer: individualOfferFactory(
          {
            isEvent: false,
            status: OfferStatus.SOLD_OUT,
          },
          individualStockFactory({
            quantity: 0,
            price: 20,
            bookingLimitDatetime: null,
          })
        ),
      }
      renderStockSection(
        props,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getByText('Votre stock est épuisé.')).toBeInTheDocument()
      expect(screen.getByText(/Quantité/)).toBeInTheDocument()
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('should render expired warning', () => {
      const props = {
        offer: individualOfferFactory(
          {
            status: OfferStatus.EXPIRED,
            isEvent: false,
          },
          individualStockFactory({
            quantity: 0,
            price: 20,
            bookingLimitDatetime: '12/02/2018',
          })
        ),
      }
      renderStockSection(
        props,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getByText('Votre stock est expiré.')).toBeInTheDocument()
      expect(screen.getByText(/Date limite de réservation/)).toBeInTheDocument()
    })

    it('should render no stock warning', () => {
      const props = {
        offer: individualOfferFactory({
          status: OfferStatus.SOLD_OUT,
          isEvent: false,
          stocks: [],
        }),
      }
      renderStockSection(
        props,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(
        screen.getByText('Vous n’avez aucun stock renseigné.')
      ).toBeInTheDocument()
      expect(screen.queryByText(/Quantité/)).not.toBeInTheDocument()
    })
  })

  describe('for stock thing', () => {
    it('should render creation summary', async () => {
      const props = {
        offer: individualOfferFactory(
          {
            status: OfferStatus.ACTIVE,
            isEvent: false,
          },
          individualStockFactory({
            quantity: 10,
            price: 20,
            bookingLimitDatetime: null,
          })
        ),
      }

      renderStockSection(
        props,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(
        screen.queryByText(/Date limite de réservation/)
      ).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer creation: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render edition summary', async () => {
      const props = {
        offer: individualOfferFactory(
          {
            status: OfferStatus.ACTIVE,
            isEvent: false,
          },
          individualStockFactory({
            quantity: 10,
            price: 20,
            bookingLimitDatetime: null,
          })
        ),
      }

      renderStockSection(props)

      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(
        screen.queryByText(/Date limite de réservation/)
      ).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(screen.getByText(/Offer edition: page stocks/)).toBeInTheDocument()
    })

    it("should render booking limit date when it's given", () => {
      const props = {
        offer: individualOfferFactory(
          {
            status: OfferStatus.EXPIRED,
          },
          individualStockFactory({
            quantity: 10,
            price: 20,
            bookingLimitDatetime: '2001-06-12',
          })
        ),
      }
      renderStockSection(props)
    })

    it('should render quantity as "Illimité" when quantity is null or undefined', () => {
      const props = {
        offer: individualOfferFactory(
          {
            status: OfferStatus.ACTIVE,
            isEvent: false,
          },
          individualStockFactory({
            quantity: null,
            price: 20,
            bookingLimitDatetime: '2001-06-12',
          })
        ),
      }

      renderStockSection(props)

      expect(screen.getByText('Illimité')).toBeInTheDocument()
    })
  })

  describe('for stock event', () => {
    it('should render creation summary', async () => {
      vi.spyOn(api, 'getStocksStats').mockResolvedValueOnce({})

      const props = {
        offer: individualOfferFactory({
          status: OfferStatus.ACTIVE,
          isEvent: true,
          stocks: [],
        }),
      }

      renderStockSection(
        props,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      await waitFor(() => {
        expect(api.getStocksStats).toHaveBeenCalled()
      })

      expect(
        screen.getByRole('heading', { name: /Dates et capacité/ })
      ).toBeInTheDocument()

      expect(
        screen.getByText('Vous n’avez aucun stock renseigné.')
      ).toBeInTheDocument()

      expect(screen.queryByText('Illimitée')).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer creation: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render edition summary', async () => {
      vi.spyOn(api, 'getStocksStats').mockResolvedValueOnce({})

      const props = {
        offer: individualOfferFactory({
          status: OfferStatus.ACTIVE,
          isEvent: true,
          stocks: [],
        }),
      }

      renderStockSection(props)

      await waitFor(() => {
        expect(api.getStocksStats).toHaveBeenCalled()
      })

      expect(
        screen.getByRole('heading', { name: /Dates et capacité/ })
      ).toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(screen.getByText(/Offer edition: page stocks/)).toBeInTheDocument()
    })
  })
})
