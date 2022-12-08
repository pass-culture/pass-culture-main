import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { ApiError, GetIndividualOfferResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
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
            mode: OFFER_WIZARD_MODE.EDITION,
            offerId: contextValue.offerId || undefined,
          }),
        ]}
      >
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
        >
          <OfferIndividualContext.Provider value={contextValue}>
            <StocksThing {...props} />
          </OfferIndividualContext.Provider>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
        >
          <div>Next page</div>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
        >
          <div>Save draft page</div>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
        >
          <div>Previous page</div>
        </Route>
        <Notification />
      </MemoryRouter>
    </Provider>
  )
}

describe('screens:StocksThing', () => {
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
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })
  it('should allow user to delete a stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    renderStockThingScreen({
      props,
      storeOverride,
      contextValue,
    })
    await userEvent.click(screen.getAllByTitle('Supprimer le stock')[1])

    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(screen.getByLabelText('Prix')).toHaveValue(null)
    expect(screen.getByText('Le stock a été supprimé.')).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })
  it('should not allow user to delete stock from a synchronized offer', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    offer.lastProvider = { id: 'PROVIDER_ID', isActive: true, name: 'Provider' }
    props.offer = { ...(offer as IOfferIndividual) }
    renderStockThingScreen({
      props,
      storeOverride,
      contextValue,
    })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    const deleteButton = screen.getAllByTitle('Supprimer le stock')[0]
    expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
    await deleteButton.click()
    expect(api.deleteStock).toHaveBeenCalledTimes(0)
    expect(screen.getByLabelText('Prix')).toHaveValue(10.01)
  })
  it('should display an error message when there is an api error', async () => {
    jest.spyOn(api, 'deleteStock').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ["There's might be an error"] }],
        } as ApiResult,
        ''
      )
    )
    renderStockThingScreen({
      props,
      storeOverride,
      contextValue,
    })

    await userEvent.click(screen.getByTestId('stock-form-actions-button-open'))
    await userEvent.click(screen.getByText('Supprimer le stock'))
    await userEvent.click(
      await screen.findByText('Supprimer', { selector: 'button' })
    )
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression du stock.'
      )
    ).toBeInTheDocument()
  })
  it('should show a success notification if nothing has been touched', async () => {
    renderStockThingScreen({ props, storeOverride, contextValue })

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: /Stock & Prix/ })
    ).not.toBeInTheDocument()
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
  })
})
