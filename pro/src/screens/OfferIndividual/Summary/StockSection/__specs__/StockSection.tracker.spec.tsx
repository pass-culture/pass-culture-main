import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { OfferStatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
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
      </MemoryRouter>
    </Provider>
  )
}

describe('Summary stock section trackers', () => {
  let props: IStockSection

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
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  it('should track creation summary (v2)', async () => {
    renderStockSection({ props, url: '/creation/recapitulatif' })

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: true,
        isEdition: false,
        offerId: 'TEST_OFFER_ID',
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track edition summary (v2)', async () => {
    renderStockSection({ props })

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: false,
        isEdition: true,
        offerId: 'TEST_OFFER_ID',
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track draft summary (v2)', async () => {
    renderStockSection({ props, url: '/brouillon/recapitulatif' })

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: true,
        isEdition: true,
        offerId: 'TEST_OFFER_ID',
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track creation summary (v3)', async () => {
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

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: true,
        isEdition: false,
        offerId: 'TEST_OFFER_ID',
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track edition summary (v3)', async () => {
    const storeOverride = {
      features: {
        initialized: true,
        list: [{ isActive: true, nameKey: 'OFFER_FORM_V3' }],
      },
    }
    renderStockSection({ props, storeOverride })
    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: false,
        isEdition: true,
        offerId: 'TEST_OFFER_ID',
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })
})
