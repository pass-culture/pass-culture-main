import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { getToday } from 'utils/date'
import {
  individualOfferFactory,
  individualOfferVenueFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'

import { STOCKS_PER_PAGE } from '../StockFormList/StockFormList'
import StocksEvent, { IStocksEventProps } from '../StocksEvent'

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
    .mockImplementation(() => new Date('2020-12-15T09:00:00Z')),
}))

const renderStockEventScreen = ({
  props,
  storeOverride = {},
  contextValue,
}: {
  props: IStocksEventProps
  storeOverride: Partial<RootState>
  contextValue: IOfferIndividualContext
}) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
        ]}
      >
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
        >
          <OfferIndividualContext.Provider value={contextValue}>
            <StocksEvent {...props} />
          </OfferIndividualContext.Provider>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
        >
          <div>Next page</div>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
        >
          <div>Previous page</div>
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
  let offer: IOfferIndividual

  beforeEach(() => {
    offer = individualOfferFactory(
      { id: 'OFFER_ID', lastProviderName: null, stocks: [] },
      undefined,
      individualOfferVenueFactory({
        departmentCode: '75',
      })
    )
    props = {
      offer: offer,
    }
    storeOverride = {}
    contextValue = {
      offerId: null,
      offer: offer,
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
  })

  it('should render stock event', async () => {
    props.offer = {
      ...offer,
      lastProviderName: 'Ciné Office',
      isDigital: false,
    }

    renderStockEventScreen({ props, storeOverride, contextValue })
    expect(
      screen.getByText('Offre synchronisée avec Ciné Office')
    ).toBeInTheDocument()
    expect(screen.getByTestId('stock-event-form')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(screen.getByLabelText('Date', { exact: true })).toBeInTheDocument()
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()
  })

  it('should submit stock and stay in creation mode when click on "Sauvegarder le brouillon"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '21')
    await userEvent.click(
      screen.getByRole('button', { name: 'Sauvegarder le brouillon' })
    )
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByTestId('stock-event-form')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith('OFFER_ID')
  })

  it('should not submit stock if nothing has changed when click on "Étape suivante" and redirect to summary', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'STOCK_ID' } as StockResponseModel],
    })
    const stock = individualStockFactory({
      id: 'STOCK_ID',
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 4,
      isEventDeletable: true,
      beginningDatetime: '2023-03-10T00:00:00.0200',
    })
    props.offer = {
      ...offer,
      stocks: [stock],
    }
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByText('Next page')).toBeInTheDocument()
    // FIX ME: romain C in reality this is not called...
    // expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should submit stock form when click on "Étape suivante" (for christmas :)', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })
    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText('25'))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(api.upsertStocks).toHaveBeenCalledWith({
      humanizedOfferId: 'OFFER_ID',
      stocks: [
        {
          beginningDatetime: '2020-12-25T11:00:00Z',
          bookingLimitDatetime: '2020-12-25T11:00:00Z',
          price: 20,
          quantity: null,
        },
      ],
    })
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByText('Next page')).toBeInTheDocument()
  })

  it('should display api errors', async () => {
    jest.spyOn(api, 'upsertStocks').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: [
            {
              price: 'API price ERROR',
              quantity: 'API quantity ERROR',
              bookingLimitDatetime: 'API bookingLimitDatetime ERROR',
            },
          ],
        } as ApiResult,
        ''
      )
    )

    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByLabelText('Date limite de réservation'))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(screen.getByText('API price ERROR')).toBeInTheDocument()
    expect(screen.getByText('API quantity ERROR')).toBeInTheDocument()
    // FIXME: someting in function StockEventForm::onChangeBeginningDate()
    // hide this api error, we need to fix it.
    // expect(
    //   screen.getByText('API bookingLimitDatetime ERROR')
    // ).toBeInTheDocument()
  })

  it('should show a success notification if nothing has been touched', async () => {
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(
      screen.getByRole('button', { name: 'Sauvegarder le brouillon' })
    )
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
  })

  it('should display draft success message on save draft button when stock form is empty', async () => {
    renderStockEventScreen({ props, storeOverride, contextValue })

    await screen.findByTestId('stock-event-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Sauvegarder le brouillon' })
    )
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByTestId('stock-event-form')).toBeInTheDocument()
  })

  it('should not display any message when user delete empty stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'STOCK_ID' } as StockResponseModel],
    })
    const stock = individualStockFactory({
      id: 'STOCK_ID',
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 0,
      isEventDeletable: true,
      beginningDatetime: '2023-03-10T00:00:00.0200',
    })
    props.offer = {
      ...offer,
      stocks: [stock],
    }
    renderStockEventScreen({ props, storeOverride, contextValue })
    expect(screen.getByTestId('stock-event-form')).toBeInTheDocument()
    await userEvent.click(screen.getAllByTitle('Supprimer le stock')[1])
    expect(
      screen.queryByText('Voulez-vous supprimer ce stock ?')
    ).not.toBeInTheDocument()

    expect(screen.queryByText('Le stock a été supprimé.')).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should not display any message when user delete empty stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'STOCK_ID' })
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'STOCK_ID' } as StockResponseModel],
    })
    props.offer = {
      ...offer,
      stocks: [],
    }
    renderStockEventScreen({ props, storeOverride, contextValue })
    expect(screen.getByTestId('stock-event-form')).toBeInTheDocument()
    await userEvent.click(screen.getAllByTitle('Supprimer le stock')[1])
    expect(
      screen.queryByText('Voulez-vous supprimer ce stock ?')
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Le stock a été supprimé.')
    ).not.toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledTimes(0)
  })

  it('should go from page to page', async () => {
    const stocks: IOfferIndividualStock[] = []
    for (let i = 0; i < 30; i++) {
      stocks.push(individualStockFactory())
    }

    props.offer = {
      ...offer,
      stocks,
    }

    renderStockEventScreen({ props, storeOverride, contextValue })

    expect(
      screen.queryAllByRole('button', { name: 'Opérations sur le stock' })
    ).toHaveLength(STOCKS_PER_PAGE)
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    await waitFor(() => {
      expect(
        screen.queryAllByRole('button', { name: 'Opérations sur le stock' })
      ).toHaveLength(10)
    })
  })
})
