import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import format from 'date-fns/format'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  OfferIndividualContext,
  OfferIndividualContextValues,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OfferIndividual, OfferIndividualVenue } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksEventEdition, {
  StocksEventEditionProps,
} from '../StocksEventEdition'

const mockLogEvent = vi.fn()

jest.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

vi.mock('utils/date', () => ({
  ...vi.importActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderStockEventScreen = (
  props: StocksEventEditionProps,
  contextValue: OfferIndividualContextValues,
  url = '/creation/stocks'
) =>
  renderWithProviders(
    <>
      <Routes>
        {['/creation/stocks', '/brouillon/stocks', '/stocks'].map(path => (
          <Route
            key={path}
            path={path}
            element={
              <OfferIndividualContext.Provider value={contextValue}>
                <StocksEventEdition {...props} />
              </OfferIndividualContext.Provider>
            }
          />
        ))}
      </Routes>
      <Notification />
    </>,
    { initialRouterEntries: [url] }
  )

const priceCategoryId = '1'

describe('screens:StocksEventEdition', () => {
  let props: StocksEventEditionProps
  let contextValue: OfferIndividualContextValues
  let offer: Partial<OfferIndividual>
  const offerId = 12

  beforeEach(() => {
    offer = {
      id: offerId,
      venue: {
        departmentCode: '75',
      } as OfferIndividualVenue,
      stocks: [],
      priceCategories: [
        { id: Number(priceCategoryId), label: 'Cat 1', price: 10 },
        { id: 2, label: 'Cat 2', price: 20 },
      ],
    }
    props = {
      offer: offer as OfferIndividual,
    }
    contextValue = {
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
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track when clicking on "Enregistrer les modifications" on edition', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockEventScreen(props, contextValue, '/stocks')

    await userEvent.type(
      screen.getByLabelText('Date'),
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire'), '12:00')
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Annuler et quitter" on edition', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockEventScreen(props, contextValue, '/stocks')

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
  })
})
