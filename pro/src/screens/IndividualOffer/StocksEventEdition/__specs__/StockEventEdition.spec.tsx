import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import format from 'date-fns/format'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  OfferStatus,
  StockResponseModel,
  StocksResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import Notification from 'components/Notification/Notification'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
import Stocks from 'pages/IndividualOfferWizard/Stocks/Stocks'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

vi.mock('utils/date', async () => {
  return {
    ...((await vi.importActual('utils/date')) ?? {}),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('screens/IndividualOffer/constants', () => ({
  MAX_STOCKS_PER_OFFER: 1,
}))

const renderStockEventScreen = async (
  apiOffer: GetIndividualOfferResponseModel
) => {
  vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  vi.spyOn(api, 'getCategories').mockResolvedValue({
    categories: [],
    subcategories: [],
  })
  vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
  vi.spyOn(api, 'upsertStocks').mockResolvedValue({} as StocksResponseModel)
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

  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        dateCreated: '2001-01-01',
        email: 'test@email.com',
        id: 12,
        roles: [],
        isEmailValidated: true,
      },
    },
  }

  renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={
            <IndividualOfferContextProvider isUserAdmin={false} offerId="BQ">
              <Stocks />
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
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
          offerId: 12,
        }),
      ],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
}

const priceCategoryId = '1'
const otherPriceCategoryId = '2'

describe('screens:StocksEventEdition', () => {
  let apiOffer: GetIndividualOfferResponseModel
  const stockToDelete = {
    beginningDatetime: '2023-01-23T08:25:31.009799Z',
    bookingLimitDatetime: '2023-01-23T07:25:31.009799Z',
    bookingsQuantity: 4,
    dateCreated: '2022-05-18T08:25:31.015652Z',
    hasActivationCode: false,
    id: 1,
    isEventDeletable: true,
    isEventExpired: false,
    isSoftDeleted: false,
    offerId: 'BQ',
    price: 10.01,
    priceCategoryId: Number(otherPriceCategoryId),
    quantity: 10,
    remainingQuantity: 6,
    activationCodesExpirationDatetime: null,
    isBookable: false,
    dateModified: '2022-05-18T08:25:31.015652Z',
    fieldsUpdated: [],
  }

  beforeEach(() => {
    apiOffer = {
      bookingEmail: null,
      dateCreated: '2022-05-18T08:25:30.991476Z',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      extraData: null,
      hasBookingLimitDatetimesPassed: true,
      isActive: true,
      isActivable: true,
      isDigital: false,
      isDuo: false,
      isEditable: true,
      isEvent: true,
      isNational: false,
      isThing: false,
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      id: 12,
      visualDisabilityCompliant: false,
      lastProvider: null,
      name: 'Séance ciné duo',
      priceCategories: [
        { id: Number(priceCategoryId), label: 'Cat 1', price: 10 },
        { id: Number(otherPriceCategoryId), label: 'Cat 2', price: 12.2 },
      ],
      stocks: [stockToDelete],
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      thumbUrl: null,
      externalTicketOfficeUrl: null,
      url: null,
      venue: {
        address: '1 boulevard Poissonnière',
        bookingEmail: 'venue29@example.net',
        city: 'Paris',
        departementCode: '75',
        id: 1,
        isVirtual: false,
        managingOfferer: {
          id: 1,
          name: 'Le Petit Rintintin Management 6',
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
    }
  })

  it('render stock event row', async () => {
    await renderStockEventScreen(apiOffer)

    expect(await screen.findByLabelText('Date')).toBeInTheDocument()
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
    expect(screen.getByLabelText('Tarif')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité restante')).toBeInTheDocument()

    expect(screen.getAllByText('Réservations')[0]).toBeInTheDocument()

    expect(
      screen.getByTestId('stock-form-actions-button-open')
    ).toBeInTheDocument()
  })

  it('should allow user to delete a stock', async () => {
    apiOffer.stocks = [
      ...apiOffer.stocks,
      {
        beginningDatetime: '2023-01-20T08:25:31.009799Z',
        bookingLimitDatetime: '2023-01-20T07:25:31.009799Z',
        bookingsQuantity: 5,
        dateCreated: '2022-05-18T08:25:31.015652Z',
        hasActivationCode: false,
        id: 1,
        isEventDeletable: true,
        isEventExpired: false,
        isSoftDeleted: false,
        price: 30.01,
        priceCategoryId: Number(otherPriceCategoryId),
        quantity: 40,
        remainingQuantity: 35,
        activationCodesExpirationDatetime: null,
        isBookable: false,
        dateModified: '2022-05-18T08:25:31.015652Z',
      },
    ]
    await renderStockEventScreen(apiOffer)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    // userEvent.dblClick to fix @reach/menu-button update, to delete after refactor
    await userEvent.dblClick(screen.getAllByText('Supprimer le stock')[0])
    expect(
      await screen.findByText('Voulez-vous supprimer cette occurrence ?')
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)

    vi.spyOn(api, 'upsertStocks')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should not allow user to delete a stock undeletable', async () => {
    apiOffer.stocks = [
      {
        ...apiOffer.stocks[0],
        isEventDeletable: false,
      },
    ]
    await renderStockEventScreen(apiOffer)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    const deleteButton = screen.getAllByTitle('Supprimer le stock')[0]
    expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
    await deleteButton.click()
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Tarif')).toHaveValue(otherPriceCategoryId)
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    await userEvent.dblClick(screen.getAllByText('Supprimer le stock')[0])
    expect(
      screen.getByText('Voulez-vous supprimer cette occurrence ?')
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should allow user to delete stock from an offer created from charlie api', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer)
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
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    await userEvent.dblClick(screen.getAllByText('Supprimer le stock')[0])
    expect(
      screen.getByText('Voulez-vous supprimer cette occurrence ?')
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    expect(
      await screen.findByText(
        'La suppression des stocks de cette offre n’est possible que depuis le logiciel synchronisé.'
      )
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should display new stocks banner for several stocks', async () => {
    await renderStockEventScreen(apiOffer)

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement'),
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire 1'), '12:15')
    await userEvent.selectOptions(
      screen.getAllByLabelText('Tarif')[1],
      priceCategoryId
    )
    await userEvent.click(screen.getByText('Valider'))

    expect(
      screen.getByText('1 nouvelle occurrence a été ajoutée')
    ).toBeInTheDocument()
  })

  it('should not allow user to add a date for a synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    expect(screen.getByText('Ajouter une ou plusieurs dates')).toBeDisabled()
  })

  it('should allow user to edit quantity for a cinema synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'ciné office',
    }
    await renderStockEventScreen(apiOffer)
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    await userEvent.type(screen.getByLabelText('Quantité restante'), '30')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      await screen.findByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
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
    await renderStockEventScreen(apiOffer)

    await userEvent.click(screen.getByTestId('stock-form-actions-button-open'))
    await userEvent.dblClick(await screen.findByText('Supprimer le stock'))

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
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
  })

  it('should save the offer without warning on "Enregistrer les modifications" button click', async () => {
    apiOffer.stocks = [
      {
        ...apiOffer.stocks[0],
        bookingsQuantity: 0,
      },
    ]
    await renderStockEventScreen(apiOffer)
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
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

  it('should show a warning when too many stock are created', async () => {
    await renderStockEventScreen(apiOffer)

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement'),
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire 1'), '12:15')
    await userEvent.selectOptions(
      screen.getAllByLabelText('Tarif')[1],
      priceCategoryId
    )
    await userEvent.click(screen.getByText('Valider'))

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )

    // when not in test 1 is replaced by MAX_STOCKS_PER_OFFER
    expect(
      await screen.findByText(
        'Veuillez créer moins de 1 occurrences par offre.'
      )
    ).toBeInTheDocument()
  })

  it('should show an error on click on "Enregistrer les modifications" when there are too many stocks', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    await renderStockEventScreen(apiOffer)

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
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a success notification if nothing has been touched', async () => {
    await renderStockEventScreen(apiOffer)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('stock-event-form')).not.toBeInTheDocument()
    expect(
      screen.getByText(/This is the read only route content/)
    ).toBeInTheDocument()
  })

  it('should not display any message when user delete empty stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    apiOffer.stocks = []
    await renderStockEventScreen(apiOffer)

    await userEvent.click(
      (await screen.findAllByTitle('Supprimer le stock'))[1]
    )
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
    await renderStockEventScreen(apiOffer)

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(
      screen.getByText('This is the read only route content')
    ).toBeInTheDocument()
  })
})
