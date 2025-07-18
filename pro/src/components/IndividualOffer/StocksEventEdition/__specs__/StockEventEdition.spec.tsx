import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as useAnalytics from 'app/App/analytics/firebase'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
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
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import { STOCKS_PER_PAGE } from 'components/StocksEventList/StocksEventList'
import { Stocks } from 'pages/IndividualOfferWizard/Stocks/Stocks'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

vi.mock('commons/utils/date', async () => {
  return {
    ...(await vi.importActual('commons/utils/date')),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockEventScreen = async (
  apiOffer: GetIndividualOfferWithAddressResponseModel,
  apiStocks: GetOfferStockResponseModel[] = [],
  stocksCount?: number,
  searchParams = ''
) => {
  vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  vi.spyOn(api, 'getCategories').mockResolvedValue({
    categories: [],
    subcategories: [],
  })
  vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
  vi.spyOn(api, 'getStocks').mockResolvedValue({
    stocks: apiStocks,
    stockCount: stocksCount ?? apiStocks.length,
    hasStocks: true,
  })
  vi.spyOn(api, 'listOffers').mockResolvedValue([listOffersOfferFactory()])

  renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={
            <IndividualOfferContextProvider>
              <Stocks />
              <ButtonLink to="/outside">Go outside !</ButtonLink>
            </IndividualOfferContextProvider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })}
          element={<div>This is the read only route content</div>}
        />
        <Route
          path="/outside"
          element={<div>This is outside stock form</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
          offerId: 12,
        }) + searchParams,
      ],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
  await waitFor(() => {
    expect(api.getStocks).toHaveBeenCalledTimes(1)
  })
}

const priceCategoryId = '1'
const otherPriceCategoryId = '2'
const mockLogEvent = vi.fn()

describe('screens:StocksEventEdition', () => {
  let apiOffer: GetIndividualOfferWithAddressResponseModel
  let apiStocks: GetOfferStockResponseModel[]

  beforeEach(() => {
    apiStocks = [
      getOfferStockFactory({
        bookingsQuantity: 4,
      }),
    ]
    apiOffer = getIndividualOfferFactory({
      bookingEmail: 'test@example.com',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      hasStocks: true,
      isActive: true,
      isDigital: false,
      isDuo: false,
      isEvent: true,
      isNational: false,
      id: 12,
      lastProvider: null,
      name: 'Séance ciné duo',
      priceCategories: [
        { id: Number(priceCategoryId), label: 'Cat 1', price: 10 },
        { id: Number(otherPriceCategoryId), label: 'Cat 2', price: 12.2 },
      ],
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      url: '',
      venue: {
        street: '1 boulevard Poissonnière',
        bookingEmail: 'venue29@example.net',
        city: 'Paris',
        departementCode: '75',
        id: 1,
        isVirtual: false,
        managingOfferer: {
          id: 1,
          name: 'Le Petit Rintintin Management 6',
          allowedOnAdage: true,
        },
        name: 'Cinéma synchro avec booking provider',
        postalCode: '75000',
        publicName: 'Cinéma synchro avec booking provider',
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
      },
      withdrawalDetails: null,
      status: OfferStatus.EXPIRED,
      withdrawalType: null,
      withdrawalDelay: null,
      bookingsCount: 0,
    })

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('render stock event row', async () => {
    await renderStockEventScreen(apiOffer, apiStocks)

    expect(screen.getByTestId('stocks.0.beginningDate')).toBeInTheDocument()
    expect(screen.getByLabelText('Tarif')).toBeInTheDocument()
    expect(
      screen.getByTestId('stocks.0.bookingLimitDatetime')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité restante')).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Supprimer' })
    ).toBeInTheDocument()
  })

  it('should allow user to delete a stock', async () => {
    const stock1 = getOfferStockFactory()
    const stock2 = getOfferStockFactory()

    await renderStockEventScreen(apiOffer, [stock1, stock2])
    vi.clearAllMocks()
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )

    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stock1.id)
    expect(api.getStocks).not.toHaveBeenCalled()

    vi.spyOn(api, 'bulkUpdateEventStocks')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(api.bulkUpdateEventStocks).not.toHaveBeenCalled()
  })

  it('should reload the page if deleting last stock of the page', async () => {
    await renderStockEventScreen(
      apiOffer,
      [getOfferStockFactory()],
      STOCKS_PER_PAGE * 5 + 10,
      '?page=3'
    )
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )

    await waitFor(() => {
      expect(api.deleteStock).toHaveBeenCalled()
    })
    expect(api.getStocks).toHaveBeenCalledWith(
      apiOffer.id,
      undefined,
      undefined,
      undefined,
      undefined,
      false,
      3
    )
  })

  it('should go to previous page if deleting last stock of the last page', async () => {
    await renderStockEventScreen(
      apiOffer,
      [getOfferStockFactory()],
      STOCKS_PER_PAGE * 5 + 1,
      '?page=6'
    )
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )

    await waitFor(() => {
      expect(api.deleteStock).toHaveBeenCalled()
      expect(api.getStocks).toHaveBeenCalledWith(
        apiOffer.id,
        undefined,
        undefined,
        undefined,
        undefined,
        false,
        5
      )
    })
  })

  it('should not allow user to delete a stock undeletable', async () => {
    await renderStockEventScreen(apiOffer, [
      { ...apiStocks[0], isEventDeletable: false },
    ])

    const deleteButton = screen.queryByRole('button', { name: 'Supprimer' })
    expect(deleteButton).not.toBeInTheDocument()
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer, apiStocks)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))
    expect(
      screen.getByText('Voulez-vous supprimer cette date ?')
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(apiStocks[0].id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should allow user to try delete stock from an offer created from public API', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer, apiStocks)
    vi.spyOn(api, 'deleteStock').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: { code: 'STOCK_FROM_CHARLIE_API_CANNOT_BE_DELETED' },
          status: 400,
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[1]
    )
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )
    expect(
      screen.getByText('Voulez-vous supprimer cette date ?')
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    expect(
      await screen.findByText(
        'La suppression des stocks de cette offre n’est possible que depuis le logiciel synchronisé.'
      )
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(apiStocks[0].id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should not allow user to add a date for a synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer, apiStocks)

    expect(screen.getByText('Ajouter une ou plusieurs dates')).toBeDisabled()
  })

  it('should allow user to edit quantity for a cinema synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'ciné office',
    }

    await renderStockEventScreen(apiOffer, apiStocks)
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: apiStocks.length,
    })

    await userEvent.type(screen.getByLabelText('Quantité restante'), '30')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(await screen.findByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(api.bulkUpdateEventStocks).toHaveBeenCalledTimes(1)
  })

  it('should let edit quantity', async () => {
    const myStocks = [
      getOfferStockFactory({
        bookingsQuantity: 0,
        quantity: 0,
        remainingQuantity: 0,
      }),
    ]

    await renderStockEventScreen(apiOffer, myStocks)
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: apiStocks.length,
    })

    await userEvent.type(screen.getByLabelText('Quantité restante'), '17')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(await screen.findByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(api.bulkUpdateEventStocks).toHaveBeenNthCalledWith(1, {
      offerId: 12,
      stocks: [
        {
          beginningDatetime: '2021-10-15T12:00:00Z',
          bookingLimitDatetime: '2021-09-15T21:59:59Z',
          id: expect.any(Number),
          priceCategoryId: 2,
          quantity: 17,
        },
      ],
    })
  })

  it('should allow user to edit quantity with 0', async () => {
    const myStocks = [
      getOfferStockFactory({
        bookingsQuantity: 0,
        quantity: 1,
        remainingQuantity: 0,
      }),
    ]

    await renderStockEventScreen(apiOffer, myStocks)
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: apiStocks.length,
    })

    await userEvent.clear(screen.getByLabelText('Quantité restante'))
    await userEvent.type(screen.getByLabelText('Quantité restante'), '0')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(await screen.findByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(api.bulkUpdateEventStocks).toHaveBeenNthCalledWith(1, {
      offerId: 12,
      stocks: [
        {
          beginningDatetime: '2021-10-15T12:00:00Z',
          bookingLimitDatetime: '2021-09-15T21:59:59Z',
          id: expect.any(Number),
          priceCategoryId: 2,
          quantity: 0,
        },
      ],
    })
  })

  it('should let edit quantity with unlimited', async () => {
    const myStocks = [
      getOfferStockFactory({
        bookingsQuantity: 0,
        quantity: 1,
        remainingQuantity: 0,
      }),
    ]

    await renderStockEventScreen(apiOffer, myStocks)
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: apiStocks.length,
    })

    await userEvent.clear(screen.getByLabelText('Quantité restante'))
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(await screen.findByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(api.bulkUpdateEventStocks).toHaveBeenNthCalledWith(1, {
      offerId: 12,
      stocks: [
        {
          beginningDatetime: '2021-10-15T12:00:00Z',
          bookingLimitDatetime: '2021-09-15T21:59:59Z',
          id: expect.any(Number),
          priceCategoryId: 2,
          quantity: null,
        },
      ],
    })
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
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))

    await userEvent.click(
      await screen.findByText('Confirmer la suppression', {
        selector: 'button',
      })
    )
    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression du stock.'
      )
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledWith(apiStocks[0].id)
  })

  it('should save the offer without warning on "Enregistrer les modifications" button click', async () => {
    const testedStock = getOfferStockFactory({
      bookingsQuantity: 0,
    })

    await renderStockEventScreen(apiOffer, [testedStock])
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: 1,
    })

    expect(screen.getByLabelText('Tarif')).toHaveValue('2')
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )
    expect(screen.getByLabelText('Tarif')).toHaveValue('1')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )

    await waitFor(() => {
      expect(
        screen.getByText('This is the read only route content')
      ).toBeInTheDocument()
    })
    expect(api.bulkUpdateEventStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a warning on click on "Enregistrer les modifications" when stock has already been booked', async () => {
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValueOnce({
      stocks_count: apiStocks.length,
    })
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )
    expect(screen.getByLabelText('Tarif')).toHaveValue(priceCategoryId)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      await screen.findByText('Des réservations sont en cours pour cette offre')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Confirmer les modifications'))
    expect(api.bulkUpdateEventStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a success notification if nothing has been touched', async () => {
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.queryByTestId('stock-event-form')).not.toBeInTheDocument()
      expect(
        screen.getByText(/This is the read only route content/)
      ).toBeInTheDocument()
    })
  })

  it('should not display any message when user delete empty stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))
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
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByText('Annuler et quitter'))

    await waitFor(() => {
      expect(
        screen.getByText('This is the read only route content')
      ).toBeInTheDocument()
    })
  })

  it('should not block when going outside and form is not touched', async () => {
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: 0,
    })

    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue({
      stocks_count: 0,
    })

    await renderStockEventScreen(apiOffer, apiStocks)
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )

    await userEvent.click(screen.getByText('Go outside !'))
    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Quitter la page'))

    expect(api.bulkUpdateEventStocks).toHaveBeenCalledTimes(0)
    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should display blocker when form is dirty', async () => {
    await renderStockEventScreen(
      apiOffer,
      [getOfferStockFactory()],
      STOCKS_PER_PAGE * 5 + 10,
      '?page=3'
    )

    await userEvent.type(screen.getByLabelText('Quantité restante'), '30')

    // should block on next page
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Quitter la page'))
    expect(screen.getByText('Page 4/6')).toBeInTheDocument()

    // should block on previous page
    await userEvent.click(
      screen.getByRole('button', { name: 'Page précédente' })
    )
    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Rester sur la page'))
    expect(screen.getByText('Page 4/6')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Page précédente' })
    )
    await userEvent.click(screen.getByText('Quitter la page'))
    expect(screen.getByText('Page 3/6')).toBeInTheDocument()
  })

  it('should trigger an event log when a filter changes', async () => {
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.selectOptions(
      screen.getByLabelText('Filtrer par tarif'),
      '1'
    )

    expect(mockLogEvent).toHaveBeenCalled()
  })
})
