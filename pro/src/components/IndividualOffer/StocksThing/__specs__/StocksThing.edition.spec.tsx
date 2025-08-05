import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { PATCH_SUCCESS_MESSAGE } from 'commons/core/shared/constants'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  listOffersOfferFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'
import { Stocks } from 'pages/IndividualOfferWizard/Stocks/Stocks'
import { Route, Routes } from 'react-router'

vi.mock('screens/IndividualOffer/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

vi.mock('commons/utils/date', async () => {
  return {
    ...(await vi.importActual('commons/utils/date')),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockThingScreen = () =>
  renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={
            <IndividualOfferContextProvider>
              <Stocks />
            </IndividualOfferContextProvider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })}
          element={<div>This is the read only route content</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
          offerId: 12,
        }),
      ],
    }
  )

describe('screens:StocksThing', () => {
  let apiOffer: GetIndividualOfferWithAddressResponseModel
  const stockToDelete = getOfferStockFactory({
    beginningDatetime: '2022-05-23T08:25:31.009799Z',
    bookingLimitDatetime: '2022-05-23T07:25:31.009799Z',
    bookingsQuantity: 4,
    hasActivationCode: false,
    id: 1,
    isEventDeletable: false,
    price: 10.01,
    quantity: 10,
    remainingQuantity: 6,
    activationCodesExpirationDatetime: null,
  })

  beforeEach(() => {
    apiOffer = getIndividualOfferFactory({
      isEvent: false,
    })

    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    vi.spyOn(api, 'getStocks').mockResolvedValue({
      stocks: [stockToDelete],
      hasStocks: true,
      stockCount: 1,
    })
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'listOffers').mockResolvedValue([listOffersOfferFactory()])
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: 0,
    })
  })

  it('should allow user to delete a stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')
    const button = screen.getByRole('button', {
      name: 'Supprimer le stock',
    })
    await userEvent.click(button)
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()

    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      await screen.findByText('This is the read only route content')
    ).toBeInTheDocument()
    expect(api.bulkUpdateEventStocks).not.toHaveBeenCalled()
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      name: 'Provider',
    }
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    const button = screen.getByRole('button', {
      name: 'Supprimer le stock',
    })
    await userEvent.click(button)
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should display an error message when there is an api error', async () => {
    vi.spyOn(api, 'deleteStock').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ["There's might be an error"] }],
        } as ApiResult,
        ''
      )
    )
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    const button = screen.getByRole('button', {
      name: 'Supprimer le stock',
    })
    await userEvent.click(button)
    await userEvent.click(
      await screen.findByText('Supprimer', { selector: 'button' })
    )
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression du stock.'
      )
    ).toBeInTheDocument()
  })

  it('should show a success notification if nothing has been touched', async () => {
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.queryByTestId('stock-thing-form')).not.toBeInTheDocument()
      expect(
        screen.getByText(/This is the read only route content/)
      ).toBeInTheDocument()
    })
  })

  it('should not display any message when user delete empty stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    vi.spyOn(api, 'getStocks').mockResolvedValue({
      stocks: [],
      hasStocks: false,
      stockCount: 0,
    })
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')
    const button = screen.getByRole('button', {
      name: 'Supprimer le stock',
    })
    await userEvent.click(button)
    expect(
      screen.queryByText('Voulez-vous supprimer ce stock ?')
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Le stock a été supprimé.')
    ).not.toBeInTheDocument()
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(api.deleteStock).toHaveBeenCalledTimes(0)
  })

  it('should go back to summary when clicking on "Annuler et quitter"', async () => {
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(
      screen.getByText('This is the read only route content')
    ).toBeInTheDocument()
  })
})
