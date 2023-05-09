import { fireEvent, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import {
  getOfferIndividualPath,
  getOfferIndividualUrl,
} from 'core/Offers/utils/getOfferIndividualUrl'
import { Stocks } from 'pages/OfferIndividualWizard/Stocks'
import { renderWithProviders } from 'utils/renderWithProviders'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderStockEventScreen = () => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        dateCreated: '2001-01-01',
        email: 'test@email.com',
        id: 'USER_ID',
        nonHumanizedId: 'ISER_ID',
        roles: [],
        isEmailValidated: true,
      },
    },
  }

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={
            <OfferIndividualContextProvider isUserAdmin={false} offerId="BQ">
              <Stocks />
            </OfferIndividualContextProvider>
          }
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={<div>Next page</div>}
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={<div>Previous page</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [
        getOfferIndividualUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
          offerId: 12,
        }),
      ],
    }
  )
}

describe('screens:StocksEventEdition', () => {
  let apiOffer: GetIndividualOfferResponseModel
  const stockToDelete = {
    beginningDatetime: '2023-01-23T08:25:31.009799Z',
    bookingLimitDatetime: '2023-01-23T07:25:31.009799Z',
    bookingsQuantity: 4,
    dateCreated: '2022-05-18T08:25:31.015652Z',
    hasActivationCode: false,
    id: 'STOCK_ID',
    nonHumanizedId: 1,
    isEventDeletable: true,
    isEventExpired: false,
    isSoftDeleted: false,
    offerId: 'BQ',
    price: 10.01,
    quantity: 10,
    remainingQuantity: 6,
    activationCodesExpirationDatetime: null,
    isBookable: false,
    dateModified: '2022-05-18T08:25:31.015652Z',
    fieldsUpdated: [],
  }

  beforeEach(() => {
    apiOffer = {
      activeMediation: null,
      bookingEmail: null,
      dateCreated: '2022-05-18T08:25:30.991476Z',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      extraData: null,
      hasBookingLimitDatetimesPassed: true,
      id: 'BQ',
      isActive: true,
      isDigital: false,
      isDuo: false,
      isEditable: true,
      isEducational: false,
      isEvent: true,
      isNational: false,
      isThing: false,
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      nonHumanizedId: 12,
      visualDisabilityCompliant: false,
      lastProvider: null,
      lastProviderId: null,
      mediaUrls: [],
      mediations: [
        {
          thumbUrl: 'http://my.thumb.url',
          credit: 'John Do',
          dateCreated: '01-01-2000',
          fieldsUpdated: [],
          id: 'AA',
          isActive: true,
          offerId: 'YA',
          thumbCount: 1,
        },
      ],
      name: 'Séance ciné duo',
      priceCategories: [{ price: 12.2, label: 'Mon premier tariff', id: 1 }],
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
        id: 'DY',
        isVirtual: false,
        lastProviderId: null,
        managingOfferer: {
          nonHumanizedId: 1,
          id: 'CU',
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

    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: [] })
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({} as StocksResponseModel)
    jest.spyOn(api, 'listOffers').mockResolvedValue([
      {
        id: 'id',
        nonHumanizedId: 1,
        status: 'ACTIVE',
        isActive: true,
        hasBookingLimitDatetimesPassed: false,
        isEducational: false,
        name: 'name',
        isEvent: false,
        venue: {
          name: 'venue',
          offererName: 'offerer',
          isVirtual: false,
          id: 'venueid',
          nonHumanizedId: 1,
          managingOffererId: '',
        },
        stocks: [],
        isEditable: true,
        isShowcase: false,
        isThing: false,
        subcategoryId: SubcategoryIdEnum.VOD,
        venueId: 'venueid',
      },
    ])
  })

  it('render stock event row', async () => {
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)

    renderStockEventScreen()

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
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    apiOffer.stocks = [
      ...apiOffer.stocks,
      {
        beginningDatetime: '2023-01-20T08:25:31.009799Z',
        bookingLimitDatetime: '2023-01-20T07:25:31.009799Z',
        bookingsQuantity: 5,
        dateCreated: '2022-05-18T08:25:31.015652Z',
        hasActivationCode: false,
        id: 'STOCK_ID_2',
        nonHumanizedId: 1,
        isEventDeletable: true,
        isEventExpired: false,
        isSoftDeleted: false,
        offerId: 'BQ',
        price: 30.01,
        quantity: 40,
        remainingQuantity: 35,
        activationCodesExpirationDatetime: null,
        isBookable: false,
        dateModified: '2022-05-18T08:25:31.015652Z',
        fieldsUpdated: [],
      },
    ]
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')
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
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.nonHumanizedId)

    jest.spyOn(api, 'upsertStocks')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
    // FIX ME: romain C in reality this is not called...
    // expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it("should allow user to delete a stock he just created (and didn't save)", async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

    // create new stock
    await userEvent.click(await screen.findByText('Ajouter une date'))
    await userEvent.type(screen.getAllByLabelText('Tarif')[0], '20')
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    // delete just created stock
    await userEvent.dblClick(screen.getAllByText('Supprimer le stock')[0])

    expect(api.deleteStock).toHaveBeenCalledTimes(0)
    expect(screen.getAllByLabelText('Tarif').length).toBe(1)
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    // FIX ME: romain C in reality this is not called...
    // expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should keep user modifications when deleting a exiting stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    const previousApiOffer = { ...apiOffer }
    const stockToDeleteId = 2
    apiOffer.stocks = [
      ...apiOffer.stocks,
      {
        beginningDatetime: '2023-01-20T08:25:31.009799Z',
        bookingLimitDatetime: '2023-01-20T07:25:31.009799Z',
        bookingsQuantity: 5,
        dateCreated: '2022-05-18T08:25:31.015652Z',
        hasActivationCode: false,
        id: 'STOCK_ID_2',
        nonHumanizedId: stockToDeleteId,
        isEventDeletable: true,
        isEventExpired: false,
        isSoftDeleted: false,
        offerId: 'BQ',
        price: 30.01,
        quantity: 40,
        remainingQuantity: 35,
        activationCodesExpirationDatetime: null,
        isBookable: false,
        dateModified: '2022-05-18T08:25:31.015652Z',
        fieldsUpdated: [],
      },
    ]
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)

    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

    // create new stock
    await userEvent.click(await screen.findByText('Ajouter une date'))
    await userEvent.type(screen.getAllByLabelText('Tarif')[0], '20')

    // delete existing stock
    jest.spyOn(api, 'getOffer').mockResolvedValue(previousApiOffer)
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[2]
    )
    await userEvent.dblClick(screen.getAllByText('Supprimer le stock')[2])
    expect(
      screen.getByText('Voulez-vous supprimer cette occurrence ?')
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByText('Confirmer la suppression', { selector: 'button' })
    )

    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDeleteId)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)

    const allPriceInputs = screen.getAllByLabelText('Tarif')
    expect(allPriceInputs).toHaveLength(2)
    expect(allPriceInputs[1]).toHaveValue(10.01)
    expect(allPriceInputs[0]).toHaveValue(20)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    jest.spyOn(api, 'upsertStocks')
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should not allow user to delete a stock undeletable', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    apiOffer.stocks = [
      {
        ...apiOffer.stocks[0],
        isEventDeletable: false,
      },
    ]
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    const deleteButton = screen.getAllByTitle('Supprimer le stock')[0]
    expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
    await deleteButton.click()
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Tarif')).toHaveValue(10.01)
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      id: 'PROVIDER_ID',
      isActive: true,
      name: 'Provider',
      enabledForPro: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

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
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.nonHumanizedId)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should not allow user to add a date for a synchronized offer', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      id: 'PROVIDER_ID',
      isActive: true,
      name: 'Provider',
      enabledForPro: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

    expect(screen.queryByText('Ajouter une date')).toBeDisabled()
  })

  it('should allow user to edit quantity for a cinema synchronized offer', async () => {
    jest
      .spyOn(api, 'upsertStocks')
      .mockResolvedValue({ stocks: [{ id: 'STOCK_ID' } as StockResponseModel] })
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      id: 'PROVIDER_ID',
      isActive: true,
      name: 'ciné office',
      enabledForPro: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')
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
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

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
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.nonHumanizedId)
  })

  it('should save the offer without warning on "Enregistrer les modifications" button click', async () => {
    jest
      .spyOn(api, 'upsertStocks')
      .mockResolvedValue({ stocks: [{ id: 'STOCK_ID' } as StockResponseModel] })
    apiOffer.stocks = [
      {
        ...apiOffer.stocks[0],
        bookingsQuantity: 0,
      },
    ]
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

    await userEvent.type(await screen.getByLabelText('Tarif'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(await screen.getByText('Next page')).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a warning on "Enregistrer les modifications" button click then save the offer', async () => {
    jest
      .spyOn(api, 'upsertStocks')
      .mockResolvedValue({ stocks: [{ id: 'STOCK_ID' } as StockResponseModel] })
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')
    // FireEvent.change instead of userEvent.type because userEvent change value but the test doesn"t work (it probably doesn't set touched at true for price field, only with inputs type number)
    fireEvent.change(screen.getByLabelText('Tarif'), {
      target: { value: '20' },
    })
    await expect(screen.getByLabelText('Tarif')).toHaveValue(20)
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
    renderStockEventScreen()
    await screen.findByTestId('stock-event-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('stock-event-form')).not.toBeInTheDocument()
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
  })
  it('should not display any message when user delete empty stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'BQ' })
    renderStockEventScreen()
    apiOffer.stocks = []
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    await screen.findByTestId('stock-event-form')
    await userEvent.click(
      (
        await screen.findAllByTitle('Supprimer le stock')
      )[1]
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

  it('should display draft success message on save button when stock form is empty and redirect to next page', async () => {
    renderStockEventScreen()
    apiOffer.stocks = []
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    await screen.findByTestId('stock-event-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('stock-event-form')).not.toBeInTheDocument()
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
  })
})
