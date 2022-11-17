import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { ButtonLink } from 'ui-kit'
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
            <ButtonLink link={{ to: '/outside', isExternal: false }}>
              Go outside !
            </ButtonLink>
          </OfferIndividualContext.Provider>
        </Route>
        <Route path="/offre/:offer_id/v3/creation/individuelle/recapitulatif">
          <div>Next page</div>
        </Route>
        <Route path="/offre/:offer_id/v3/creation/individuelle/stocks">
          <div>Save draft page</div>
        </Route>
        <Route path="/offre/:offer_id/v3/creation/individuelle/informations">
          <div>Previous page</div>
        </Route>
        <Route path="/outside">
          <div>This is outside stock form</div>
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

  it('should not block when submitting stock when clicking on "Sauvegarder le brouillon"', async () => {
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
    expect(screen.getByText('Save draft page')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith('OFFER_ID')
  })

  it('should not block and submit stock form when click on "Étape suivante"', async () => {
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
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Next page')).toBeInTheDocument()
  })

  it('should not block when going outside and form is not touched', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should block when clicking on "Étape précédente"', async () => {
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
      screen.getByRole('button', { name: 'Étape précédente' })
    )
    await userEvent.click(screen.getByText('Quitter'))

    expect(await screen.findByText('Previous page')).toBeInTheDocument()
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should be able to stay on stock form after click on "Annuler"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Annuler'))

    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Quitter'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(0)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to submit from RouteLeavingGuard in draft', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
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

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées dans votre brouillon.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to submit from RouteLeavingGuard in edition', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stockIds: [{ id: 'CREATED_STOCK_ID' }],
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

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées.'
      )
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getAllByText('Enregistrer les modifications')[1]
    )
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })
})
