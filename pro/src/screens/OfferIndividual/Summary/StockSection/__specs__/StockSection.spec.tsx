import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route } from 'react-router'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import StockSection, { IStockSection } from '../StockSection'

const mockLogEvent = jest.fn()

const renderStockSection = (
  props: IStockSection,
  url: string = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.EDITION,
  })
) =>
  renderWithProviders(
    <>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.EDITION,
        })}
      >
        <StockSection {...props} />
      </Route>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
      >
        <StockSection {...props} />
      </Route>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.DRAFT,
        })}
      >
        <StockSection {...props} />
      </Route>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
      >
        <div>Offer V3 creation: page stocks</div>
      </Route>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
        })}
      >
        <div>Offer V3 edition: page stocks</div>
      </Route>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        })}
      >
        <div>Offer V3 brouillon: page stocks</div>
      </Route>
    </>,
    { initialRouterEntries: [url] }
  )

describe('Summary stock section', () => {
  let props: IStockSection

  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  describe('for general case', () => {
    it('should render sold out warning', async () => {
      props = {
        stockThing: {
          quantity: 0,
          price: 20,
          bookingLimitDatetime: null,
        },
        offerId: 'TEST_OFFER_ID',
        offerStatus: OfferStatus.SOLD_OUT,
      }
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
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

    it('should render expired warning', async () => {
      props = {
        stockThing: {
          quantity: 0,
          price: 20,
          bookingLimitDatetime: '12/02/2018',
        },
        offerId: 'TEST_OFFER_ID',
        offerStatus: OfferStatus.EXPIRED,
      }
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
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

    it('should render no stock warning', async () => {
      props = {
        offerId: 'TEST_OFFER_ID',
        offerStatus: OfferStatus.SOLD_OUT,
      }
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
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
    beforeEach(() => {
      props = {
        stockThing: {
          quantity: 10,
          price: 20,
          bookingLimitDatetime: null,
        },
        offerId: 'TEST_OFFER_ID',
        offerStatus: OfferStatus.ACTIVE,
      }
    })

    it('should render creation summary (v3)', async () => {
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
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
        screen.getByText(/Offer V3 creation: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render edition summary (v3)', async () => {
      renderStockSection(props)
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(
        screen.queryByText(/Date limite de réservation/)
      ).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V3 edition: page stocks/)
      ).toBeInTheDocument()
    })

    it("should render booking limit date when it's given", async () => {
      props = {
        ...props,
        stockThing: {
          quantity: 10,
          price: 20,
          bookingLimitDatetime: '2001-06-12',
        },
      }
      renderStockSection(props)
      expect(screen.getByText(/Date limite de réservation/)).toBeInTheDocument()
    })

    it.each([null, undefined])(
      'should render quantity as "Illimité" when quantity is null or undefined',
      async quantity => {
        props = {
          ...props,
          stockThing: {
            quantity: quantity,
            price: 20,
            bookingLimitDatetime: '2001-06-12',
          },
        }

        renderStockSection(props)
        expect(screen.getByText('Illimité')).toBeInTheDocument()
      }
    )
  })

  describe('for stock event', () => {
    beforeEach(() => {
      props = {
        stockEventList: [
          {
            quantity: 10,
            price: 20,
            bookingLimitDatetime: '12/03/2020',
            beginningDatetime: '12/03/2020',
            departmentCode: '78',
          },
          {
            quantity: 10,
            price: 20,
            bookingLimitDatetime: '12/03/2020',
            beginningDatetime: '12/03/2020',
            departmentCode: '78',
          },
        ],
        offerId: 'TEST_OFFER_ID',
        offerStatus: OfferStatus.ACTIVE,
      }
    })

    it('should render creation summary (v3)', async () => {
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(2)

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V3 creation: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render brouillon summary (v3)', async () => {
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: 'AA' }
        )
      )
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(2)

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V3 brouillon: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render edition summary (v3)', async () => {
      renderStockSection(props)
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(2)

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V3 edition: page stocks/)
      ).toBeInTheDocument()
    })

    it('should display or not all stocks', async () => {
      props.stockEventList = [
        {
          quantity: 10,
          price: 20,
          bookingLimitDatetime: '12/03/2020',
          beginningDatetime: '12/03/2020',
          departmentCode: '78',
        },
        {
          quantity: 10,
          price: 20,
          bookingLimitDatetime: '12/03/2020',
          beginningDatetime: '12/03/2020',
          departmentCode: '78',
        },
        {
          quantity: null,
          price: 20,
          bookingLimitDatetime: '12/03/2020',
          beginningDatetime: '12/03/2020',
          departmentCode: '78',
        },
      ]
      renderStockSection(
        props,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(2)
      const displayMore = screen.getByText('Afficher plus de dates')

      await userEvent.click(displayMore)
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(3)
      expect(screen.getAllByText(/Illimité/)).toHaveLength(1)
    })
  })
})
