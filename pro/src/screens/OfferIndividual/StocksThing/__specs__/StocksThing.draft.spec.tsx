import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import {
  IOfferIndividual,
  IOfferIndividualStock,
  IOfferIndividualVenue,
} from 'core/Offers/types'
import {
  getOfferIndividualPath,
  getOfferIndividualUrl,
} from 'core/Offers/utils/getOfferIndividualUrl'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import StocksThing, { IStocksThingProps } from '../StocksThing'

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

const renderStockThingScreen = ({
  props,
  storeOverride = {},
  contextValue,
}: {
  props: IStocksThingProps
  storeOverride: Partial<RootState>
  contextValue: IOfferIndividualContext
}) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          getOfferIndividualUrl({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
            offerId: contextValue.offerId || undefined,
          }),
        ]}
      >
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
        >
          <OfferIndividualContext.Provider value={contextValue}>
            <StocksThing {...props} />
          </OfferIndividualContext.Provider>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
        >
          <div>Next page</div>
        </Route>
        <Notification />
      </MemoryRouter>
    </Provider>
  )
}

describe('screens:StocksThing::draft', () => {
  let props: IStocksThingProps
  let storeOverride: Partial<RootState>
  let contextValue: IOfferIndividualContext
  let offer: Partial<IOfferIndividual>
  let stock: Partial<IOfferIndividualStock>

  beforeEach(() => {
    stock = {
      id: 'STOCK_ID',
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 4,
      isEventDeletable: true,
    }
    offer = {
      id: 'OFFER_ID',
      lastProvider: null,
      venue: {
        departmentCode: '75',
      } as IOfferIndividualVenue,
      stocks: [stock as IOfferIndividualStock],
    }
    props = {
      offer: offer as IOfferIndividual,
    }
    storeOverride = {}
    contextValue = {
      offerId: 'OFFER_ID',
      offer: offer as IOfferIndividual,
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
    jest.spyOn(api, 'upsertStocks')
  })

  it('should show a success notification if nothing has been touched', async () => {
    renderStockThingScreen({ props, storeOverride, contextValue })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Sauvegarder le brouillon',
      })
    )

    expect(api.upsertStocks).not.toHaveBeenCalled()
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByTestId('stock-thing-form')).toBeInTheDocument()
    expect(screen.queryByText(/Next page/)).not.toBeInTheDocument()
  })

  it('should show a success notification if nothing has been touched and click on next step', async () => {
    renderStockThingScreen({ props, storeOverride, contextValue })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Étape suivante',
      })
    )

    expect(api.upsertStocks).not.toHaveBeenCalled()
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('stock-thing-form')).not.toBeInTheDocument()
    expect(screen.queryByText(/Next page/)).toBeInTheDocument()
  })
})
