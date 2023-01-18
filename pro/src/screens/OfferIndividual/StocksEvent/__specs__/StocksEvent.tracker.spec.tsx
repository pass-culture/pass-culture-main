import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { getToday } from 'utils/date'

import StocksEvent, { IStocksEventProps } from '../StocksEvent'

const mockLogEvent = jest.fn()

jest.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: jest.fn(),
  }
})

jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderStockEventScreen = ({
  props,
  storeOverride = {},
  contextValue,
  url = '/creation/stocks',
}: {
  props: IStocksEventProps
  storeOverride: Partial<RootState>
  contextValue: IOfferIndividualContext
  url?: string
}) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route path={['/creation/stocks', '/brouillon/stocks', '/stocks']}>
          <OfferIndividualContext.Provider value={contextValue}>
            <StocksEvent {...props} />
          </OfferIndividualContext.Provider>
        </Route>
        <Notification />
      </MemoryRouter>
    </Provider>
  )
}

const today = getToday()

describe('screens:StocksEvent', () => {
  let props: IStocksEventProps
  let storeOverride: Partial<RootState>
  let contextValue: IOfferIndividualContext
  let offer: Partial<IOfferIndividual>

  beforeEach(() => {
    offer = {
      id: 'OFFER_ID',
      venue: {
        departmentCode: '75',
      } as IOfferIndividualVenue,
      stocks: [],
    }
    props = {
      offer: offer as IOfferIndividual,
    }
    storeOverride = {}
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
      isFirstOffer: false,
      venuesMissingReimbursementPoint: {},
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track when clicking on "Sauvegarder le brouillon" on creation', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: 'OFFER_ID',
        to: 'stocks',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when clicking on "Sauvegarder le brouillon" on draft', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: '/brouillon/stocks',
    })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: 'OFFER_ID',
        to: 'stocks',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when clicking on "Enregistrer les modifications" on edition', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: '/stocks',
    })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: 'OFFER_ID',
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape suivante" on creation', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: 'OFFER_ID',
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape suivante" on draft', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: '/brouillon/stocks/',
    })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: 'OFFER_ID',
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape précédente" on creation', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: 'OFFER_ID',
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape précédente" on draft', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: '/brouillon/stocks',
    })

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: 'OFFER_ID',
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Annuler et quitter" on edition', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: '/stocks',
    })

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: 'OFFER_ID',
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
  })
})
