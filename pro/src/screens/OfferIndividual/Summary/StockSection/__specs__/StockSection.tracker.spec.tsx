import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StockSection, { IStockSection } from '../StockSection'

const mockLogEvent = jest.fn()

const renderStockSection = (props: IStockSection, url = '/recapitulatif') =>
  renderWithProviders(
    <Routes>
      <Route path="/recapitulatif" element={<StockSection {...props} />} />
      <Route
        path="/creation/recapitulatif"
        element={<StockSection {...props} />}
      />
      <Route
        path="/brouillon/recapitulatif"
        element={<StockSection {...props} />}
      />
    </Routes>,
    { initialRouterEntries: [url] }
  )

describe('Summary stock section trackers', () => {
  let props: IStockSection
  const offerId = 1

  beforeEach(() => {
    props = {
      offer: individualOfferFactory(
        {
          status: OfferStatus.ACTIVE,
          nonHumanizedId: offerId,
        },
        individualStockFactory({
          quantity: 10,
          price: 20,
          bookingLimitDatetime: null,
        })
      ),
    }
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track creation summary (v2)', async () => {
    renderStockSection(props, '/creation/recapitulatif')

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track edition summary (v2)', async () => {
    renderStockSection(props)

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track draft summary (v2)', async () => {
    renderStockSection(props, '/brouillon/recapitulatif')

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track creation summary (v3)', async () => {
    renderStockSection(props, '/creation/recapitulatif')

    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })

  it('should track edition summary (v3)', async () => {
    renderStockSection(props)
    await userEvent.click(screen.getByRole('link', { name: /Modifier/ }))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'recapitulatif',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: 'stocks',
        used: 'RecapLink',
      }
    )
  })
})
