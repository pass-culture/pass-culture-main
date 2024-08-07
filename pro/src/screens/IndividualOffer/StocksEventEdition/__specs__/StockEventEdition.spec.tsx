import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { format } from 'date-fns'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

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
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import { STOCKS_PER_PAGE } from 'components/StocksEventList/StocksEventList'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { Stocks } from 'pages/IndividualOfferWizard/Stocks/Stocks'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

vi.mock('utils/date', async () => {
  return {
    ...(await vi.importActual('utils/date')),
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
  vi.spyOn(api, 'listOffers').mockResolvedValue([
    {
      id: 1,
      status: OfferStatus.ACTIVE,
      isActive: true,
      hasBookingLimitDatetimesPassed: false,
      isEducational: false,
      name: 'name',
      isEvent: false,
      venue: {
        name: 'venue',
        offererName: 'offerer',
        isVirtual: false,
        id: 1,
      },
      stocks: [],
      isEditable: true,
      isShowcase: false,
      isThing: false,
      subcategoryId: SubcategoryIdEnum.VOD,
    },
  ])

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
      isActivable: true,
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
      externalTicketOfficeUrl: '',
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
  })

  it('render stock event row', async () => {
    await renderStockEventScreen(apiOffer, apiStocks)

    expect(await screen.findByLabelText('Date *')).toBeInTheDocument()
    expect(screen.getByLabelText('Horaire *')).toBeInTheDocument()
    expect(screen.getByLabelText('Tarif *')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation *')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité restante *')).toBeInTheDocument()

    expect(screen.getAllByText('Réservations *')[0]).toBeInTheDocument()

    expect(screen.getByTestId('dropdown-menu-trigger')).toBeInTheDocument()
  })

  it('should allow user to delete a stock', async () => {
    const stock1 = getOfferStockFactory()
    const stock2 = getOfferStockFactory()

    await renderStockEventScreen(apiOffer, [stock1, stock2])
    vi.clearAllMocks()
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[0])
    await userEvent.click(screen.getByTitle('Supprimer le stock'))

    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stock1.id)
    expect(api.getStocks).not.toHaveBeenCalled()

    vi.spyOn(api, 'upsertStocks')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should reload the page if deleting last stock of the page', async () => {
    await renderStockEventScreen(
      apiOffer,
      [getOfferStockFactory()],
      STOCKS_PER_PAGE * 5 + 10,
      '?page=3'
    )
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[0])
    await userEvent.click(screen.getByTitle('Supprimer le stock'))

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

    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[0])
    await userEvent.click(screen.getByTitle('Supprimer le stock'))

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
      5
    )
  })

  it('should not allow user to delete a stock undeletable', async () => {
    await renderStockEventScreen(apiOffer, [
      { ...apiStocks[0], isEventDeletable: false },
    ])

    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    const deleteButton = screen.getByTitle('Supprimer le stock')
    expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
    await userEvent.click(deleteButton)
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Tarif *')).toHaveValue(otherPriceCategoryId)
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer, apiStocks)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    await userEvent.click(screen.getByTitle('Supprimer le stock'))
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

  it('should allow user to try delete stock from an offer created from charlie api', async () => {
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

    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[1])
    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[0])
    await userEvent.click(screen.getByTitle('Supprimer le stock'))
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

  it('should display new stocks notification when creating new stock', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValueOnce({
      stocks_count: apiStocks.length,
    })
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '14:15')
    await userEvent.selectOptions(
      screen.getAllByLabelText('Tarif *')[1],
      priceCategoryId
    )
    await userEvent.click(screen.getByText('Valider'))

    expect(
      screen.getByText('1 nouvelle date a été ajoutée')
    ).toBeInTheDocument()
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
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks_count: apiStocks.length,
    })

    await userEvent.type(screen.getByLabelText('Quantité restante *'), '30')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(await screen.findByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
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

    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    await userEvent.click(await screen.findByText('Supprimer le stock'))

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
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks_count: 1,
    })

    await userEvent.selectOptions(
      screen.getByLabelText('Tarif *'),
      priceCategoryId
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('This is the read only route content')
    ).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a warning on click on "Enregistrer les modifications" when stock has already been booked', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValueOnce({
      stocks_count: apiStocks.length,
    })
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.selectOptions(
      screen.getByLabelText('Tarif *'),
      priceCategoryId
    )
    expect(screen.getByLabelText('Tarif *')).toHaveValue(priceCategoryId)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      await screen.findByText('Des réservations sont en cours pour cette offre')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Confirmer les modifications'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a success notification if nothing has been touched', async () => {
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(screen.queryByTestId('stock-event-form')).not.toBeInTheDocument()
    expect(
      screen.getByText(/This is the read only route content/)
    ).toBeInTheDocument()
  })

  it('should not display any message when user delete empty stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    await userEvent.click(screen.getByTitle('Supprimer le stock'))
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

    expect(
      screen.getByText('This is the read only route content')
    ).toBeInTheDocument()
  })

  it('should not block when going outside and form is not touched', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks_count: 0,
    })

    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks_count: 0,
    })

    await renderStockEventScreen(apiOffer, apiStocks)
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif *'),
      priceCategoryId
    )

    await userEvent.click(screen.getByText('Go outside !'))
    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Quitter la page'))

    expect(api.upsertStocks).toHaveBeenCalledTimes(0)
    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should display blocker when form is dirty', async () => {
    await renderStockEventScreen(
      apiOffer,
      [getOfferStockFactory()],
      STOCKS_PER_PAGE * 5 + 10,
      '?page=3'
    )
    await userEvent.type(screen.getByLabelText('Quantité restante *'), '30')

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
})
