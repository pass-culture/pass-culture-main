import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import * as useAnalytics from 'hooks/useAnalytics'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import StockThingSection, {
  IStockThingSummarySection,
} from '../StockThingSection'

const mockLogEvent = jest.fn()

const renderStockThingSection = ({
  props,
  storeOverride = {},
  url = '/summary',
}: {
  props: IStockThingSummarySection
  storeOverride?: Partial<RootState>
  url?: string
}) => {
  const store = configureTestStore({
    ...{
      user: {
        currentUser: { publicName: 'My Test User PublicName', isAdmin: false },
        initialized: true,
      },
    },
    ...storeOverride,
  })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route path="/summary">
          <StockThingSection {...props} />
        </Route>
        <Route path="/offre/:offerId/v3/creation/individuelle/stocks">
          <div>Offer V3 creation: page stocks</div>
        </Route>
        <Route path="/offre/:offerId/v3/individuelle/stocks">
          <div>Offer V3 edition: page stocks</div>
        </Route>

        <Route path="/offre/:offerId/individuel/creation/stocks">
          <div>Offer V2 creation: page stocks</div>
        </Route>
        <Route path="/offre/:offerId/individuel/stocks">
          <div>Offer V2 edition: page stocks</div>
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('OfferIndividual section: venue', () => {
  let props: IStockThingSummarySection

  beforeEach(() => {
    props = {
      quantity: 10,
      price: 20,
      bookingLimitDatetime: null,
      isCreation: false,
      offerId: 'TEST_OFFER_ID',
      isDraft: true,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should render creation summary (v2)', async () => {
    props = {
      ...props,
      isCreation: true,
    }
    renderStockThingSection({ props })
    expect(
      screen.getByRole('heading', { name: /Stocks et prix/ })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
    expect(
      screen.getByText(/Offer V2 creation: page stocks/)
    ).toBeInTheDocument()
  })

  it('should render edition summary (v2)', async () => {
    props = {
      ...props,
      isCreation: false,
      isDraft: false,
    }
    renderStockThingSection({ props })
    expect(
      screen.getByRole('heading', { name: /Stocks et prix/ })
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))
    expect(
      screen.getByText(/Offer V2 edition: page stocks/)
    ).toBeInTheDocument()
  })

  it('should render creation summary (v3)', async () => {
    const storeOverride = {
      features: {
        initialized: true,
        list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
      },
    }
    props = {
      ...props,
      isCreation: true,
    }
    renderStockThingSection({ props, storeOverride })
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
    props = {
      ...props,
      isCreation: false,
    }
    renderStockThingSection({ props, storeOverride })
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
      bookingLimitDatetime: '2001-06-12',
    }
    renderStockThingSection({ props, storeOverride })
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
        bookingLimitDatetime: '2001-06-12',
        quantity,
      }

      renderStockThingSection({ props, storeOverride })
      expect(screen.getByText('Illimité')).toBeInTheDocument()
    }
  )
})
