import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import * as useAnalytics from 'hooks/useAnalytics'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import StockSection, { IStockSection } from '../StockSection'

const mockLogEvent = jest.fn()

const renderStockSection = ({
  props,
  storeOverride = {},
  url = '/recapitulatif',
}: {
  props: IStockSection
  storeOverride?: Partial<RootState>
  url?: string
}) => {
  const store = configureTestStore({
    ...storeOverride,
  })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route path="/recapitulatif">
          <StockSection {...props} />
        </Route>
        <Route path="/creation/recapitulatif">
          <StockSection {...props} />
        </Route>
        <Route path="/brouillon/recapitulatif">
          <StockSection {...props} />
        </Route>
        <Route path="/offre/:offerId/v3/creation/individuelle/stocks">
          <div>Offer V3 creation: page stocks</div>
        </Route>
        <Route path="/offre/:offerId/v3/individuelle/stocks">
          <div>Offer V3 edition: page stocks</div>
        </Route>
        <Route path="/offre/:offerId/v3/brouillon/individuelle/stocks">
          <div>Offer V3 brouillon: page stocks</div>
        </Route>

        <Route path="/offre/:offerId/individuel/creation/stocks">
          <div>Offer V2 creation: page stocks</div>
        </Route>
        <Route path="/offre/:offerId/individuel/stocks">
          <div>Offer V2 edition: page stocks</div>
        </Route>
        <Route path="/offre/:offerId/individuel/brouillon/stocks">
          <div>Offer V2 brouillon: page stocks</div>
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('Summary stock section', () => {
  let props: IStockSection

  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
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
      }
    })

    it('should render creation summary (v2)', async () => {
      renderStockSection({ props, url: '/creation/recapitulatif' })
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V2 creation: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render edition summary (v2)', async () => {
      renderStockSection({ props })
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V2 edition: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render draft summary (v2)', async () => {
      renderStockSection({ props, url: '/brouillon/recapitulatif' })
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()

      await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
      expect(
        screen.getByText(/Offer V2 brouillon: page stocks/)
      ).toBeInTheDocument()
    })

    it('should render creation summary (v3)', async () => {
      const storeOverride = {
        features: {
          initialized: true,
          list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
        },
      }
      renderStockSection({
        props,
        storeOverride,
        url: '/creation/recapitulatif',
      })
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
      const storeOverride = {
        features: {
          initialized: true,
          list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
        },
      }
      renderStockSection({ props, storeOverride })
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
      const storeOverride = {
        features: {
          initialized: true,
          list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
        },
      }

      props = {
        ...props,
        stockThing: {
          quantity: 10,
          price: 20,
          bookingLimitDatetime: '2001-06-12',
        },
      }
      renderStockSection({ props, storeOverride })
      expect(screen.getByText(/Date limite de réservation/)).toBeInTheDocument()
    })

    it.each([null, undefined])(
      'should render quantity as "Illimité" when quantity is null or undefined',
      async quantity => {
        const storeOverride = {
          features: {
            initialized: true,
            list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
          },
        }
        props = {
          ...props,
          stockThing: {
            quantity: quantity,
            price: 20,
            bookingLimitDatetime: '2001-06-12',
          },
        }

        renderStockSection({ props, storeOverride })
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
      }
    })

    it('should render creation summary (v3)', async () => {
      const storeOverride = {
        features: {
          initialized: true,
          list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
        },
      }
      renderStockSection({
        props,
        storeOverride,
        url: '/creation/recapitulatif',
      })
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
      const storeOverride = {
        features: {
          initialized: true,
          list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
        },
      }
      renderStockSection({
        props,
        storeOverride,
        url: '/brouillon/recapitulatif',
      })
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
      const storeOverride = {
        features: {
          initialized: true,
          list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
        },
      }
      renderStockSection({ props, storeOverride })
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
          quantity: 10,
          price: 20,
          bookingLimitDatetime: '12/03/2020',
          beginningDatetime: '12/03/2020',
          departmentCode: '78',
        },
      ]
      renderStockSection({
        props,
        url: '/creation/recapitulatif',
      })
      expect(
        screen.getByRole('heading', { name: /Stocks et prix/ })
      ).toBeInTheDocument()
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(2)
      const displayMore = screen.getByText('Afficher plus de dates')

      await userEvent.click(displayMore)
      expect(screen.getAllByText(/Date limite de réservation/)).toHaveLength(3)
    })
  })
})
