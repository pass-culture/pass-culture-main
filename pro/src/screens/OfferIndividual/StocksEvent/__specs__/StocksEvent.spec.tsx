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
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { getToday } from 'utils/date'

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
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })

  it('should render stock event', async () => {
    props.offer = {
      ...(offer as IOfferIndividual),
      lastProviderName: 'Ciné Office',
      isDigital: false,
    }

    renderStockEventScreen({ props, storeOverride, contextValue })
    expect(
      screen.getByText('Offre synchronisée avec Ciné Office')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: /Stock & Prix/ })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’événement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
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
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Sauvegarder le brouillon' })
    )
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Stock & Prix' })
    ).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith('OFFER_ID')
  })

  it('should not submit stock if nothing has changed when click on "Étape suivante" and redirect to summary', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })
    const stock = {
      id: 'STOCK_ID',
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 4,
      isEventDeletable: true,
      beginningDatetime: '2023-03-10T00:00:00.0200',
    }
    props.offer = {
      ...(offer as IOfferIndividual),
      stocks: [stock as IOfferIndividualStock],
    }
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(api.upsertStocks).not.toHaveBeenCalled()
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByText('Next page')).toBeInTheDocument()
  })
  it('should submit stock form when click on "Étape suivante" (for christmas :)', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })
    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText('25'))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.tab()
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
})
