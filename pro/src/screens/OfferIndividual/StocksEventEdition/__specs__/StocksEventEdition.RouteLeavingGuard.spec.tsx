import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import { getToday } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksEventEdition, {
  StocksEventEditionProps,
} from '../StocksEventEdition'

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

const renderStockEventScreen = (
  props: StocksEventEditionProps,
  contextValue: IOfferIndividualContext,
  url: string = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })
) =>
  renderWithProviders(
    <>
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode,
            })}
            element={
              <OfferIndividualContext.Provider value={contextValue}>
                <StocksEventEdition {...props} />
                <ButtonLink link={{ to: '/outside', isExternal: false }}>
                  Go outside !
                </ButtonLink>
              </OfferIndividualContext.Provider>
            }
          />
        ))}
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Next page</div>}
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Save draft page</div>}
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Previous page</div>}
        />
        <Route
          path="/outside"
          element={<div>This is outside stock form</div>}
        />
      </Routes>
      <Notification />
    </>,
    { initialRouterEntries: [url] }
  )

const today = getToday()
const priceCategoryId = '1'

describe('screens:StocksEventEdition', () => {
  let props: StocksEventEditionProps
  let contextValue: IOfferIndividualContext
  let offer: Partial<IOfferIndividual>
  const offerId = 1

  beforeEach(() => {
    offer = {
      nonHumanizedId: offerId,
      venue: {
        departmentCode: '75',
      } as IOfferIndividualVenue,
      stocks: [],
      priceCategories: [
        { id: Number(priceCategoryId), label: 'Cat 1', price: 10 },
        { id: 2, label: 'Cat 2', price: 20 },
      ],
    }
    props = {
      offer: offer as IOfferIndividual,
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
      shouldTrack: false,
      showVenuePopin: {},
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should not block when going outside and form is not touched', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen(props, contextValue)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen(props, contextValue)
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Quitter la page'))

    expect(api.upsertStocks).toHaveBeenCalledTimes(0)
    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should track when quitting without submit from RouteLeavingGuard', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen(props, contextValue)

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Quitter la page'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: '/outside',
        used: 'RouteLeavingGuard',
      }
    )
  })
})
