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
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { LIVRE_PAPIER_SUBCATEGORY_ID } from 'core/Offers'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import Notification from 'new_components/Notification/Notification'
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
      <MemoryRouter initialEntries={['/creation/stocks']}>
        <Route path="/creation/stocks">
          <OfferIndividualContext.Provider value={contextValue}>
            <StocksThing {...props} />
          </OfferIndividualContext.Provider>
        </Route>
        <Route path="/offre/:offer_id/v3/creation/individuelle/recapitulatif">
          <div>Next page</div>
        </Route>
        <Route path="/offres">
          <div>Save draft page</div>
        </Route>
        <Route path="/offre/:offer_id/v3/creation/individuelle/informations">
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

  it('should render physical stock thing', async () => {
    props.offer = {
      ...(offer as IOfferIndividual),
      isDigital: false,
    }

    renderStockThingScreen({ props, storeOverride, contextValue })
    expect(
      screen.getByRole('heading', { name: /Stock & Prix/ })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Les utilisateurs ont 30 jours pour annuler leurs réservations d’offres numériques. Dans le cas d’offres avec codes d’activation, les utilisateurs ne peuvent pas annuler leurs réservations d’offres numériques. Toute réservation est définitive et sera immédiatement validée.'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()
  })
  it('should render digital stock thing', async () => {
    props.offer = {
      ...(offer as IOfferIndividual),
      subcategoryId: 'TESTID',
      isDigital: true,
    }
    renderStockThingScreen({ props, storeOverride, contextValue })
    expect(
      screen.getByText(
        'Les utilisateurs ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()
  })
  it('should render digital book', async () => {
    props.offer = {
      ...(offer as IOfferIndividual),
      subcategoryId: LIVRE_PAPIER_SUBCATEGORY_ID,
      isDigital: true,
    }
    renderStockThingScreen({ props, storeOverride, contextValue })
    expect(
      screen.getByText(
        'Les utilisateurs ont 10 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()
  })

  it('should submit stock form when click on "Étape suivante""', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })
    renderStockThingScreen({ props, storeOverride, contextValue })

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(api.upsertStocks).toHaveBeenCalledWith({
      humanizedOfferId: 'OFFER_ID',
      stocks: [
        {
          bookingLimitDatetime: null,
          price: 20,
          quantity: null,
        },
      ],
    })
    expect(
      screen.getByText('Vos modifications ont bien été prises en compte')
    ).toBeInTheDocument()
    expect(screen.getByText('Next page')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith('OFFER_ID')
  })

  it('should submit stock form when click on "Étape précédente"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })

    renderStockThingScreen({ props, storeOverride, contextValue })

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape précédente' })
    )
    expect(api.upsertStocks).toHaveBeenCalledWith({
      humanizedOfferId: 'OFFER_ID',
      stocks: [
        {
          bookingLimitDatetime: null,
          price: 20,
          quantity: null,
        },
      ],
    })
    expect(
      screen.getByText('Vos modifications ont bien été prises en compte')
    ).toBeInTheDocument()
    expect(screen.getByText('Previous page')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith('OFFER_ID')
  })

  it('should display api errors', async () => {
    jest.spyOn(api, 'upsertStocks').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            price: 'API price ERROR',
            quantity: 'API quantity ERROR',
            bookingLimitDatetime: 'API bookingLimitDatetime ERROR',
          },
        } as ApiResult,
        ''
      )
    )

    renderStockThingScreen({ props, storeOverride, contextValue })

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )
    expect(screen.getByText('API price ERROR')).toBeInTheDocument()
    expect(screen.getByText('API quantity ERROR')).toBeInTheDocument()
    expect(
      screen.getByText('API bookingLimitDatetime ERROR')
    ).toBeInTheDocument()
  })
})
