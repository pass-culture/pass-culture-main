import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import format from 'date-fns/format'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
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
import { individualGetOfferStockResponseModelFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

vi.mock('utils/date', async () => {
  return {
    ...((await vi.importActual('utils/date')) ?? {}),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockEventScreen = async (
  apiOffer: GetIndividualOfferResponseModel,
  apiStocks: GetOfferStockResponseModel[] = []
) => {
  vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  vi.spyOn(api, 'getCategories').mockResolvedValue({
    categories: [],
    subcategories: [],
  })
  vi.spyOn(api, 'getStocks').mockResolvedValue({
    stocks: apiOffer.stocks,
    stock_count: 2,
  })
  vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
  vi.spyOn(api, 'getStocks').mockResolvedValue({
    stocks: apiStocks,
    stock_count: apiStocks.length,
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

  const storeOverrides = {
    user: {
      currentUser: {
        isAdmin: false,
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
  let apiStocks: GetOfferStockResponseModel[]

  beforeEach(() => {
    apiStocks = [
      individualGetOfferStockResponseModelFactory({
        beginningDatetime: '2023-01-23T08:25:31.009799Z',
        bookingLimitDatetime: '2023-01-23T07:25:31.009799Z',
        bookingsQuantity: 4,
        dateCreated: '2022-05-18T08:25:31.015652Z',
        hasActivationCode: false,
        id: 1,
        isEventDeletable: true,
        isEventExpired: false,
        isSoftDeleted: false,
        price: 10.01,
        priceCategoryId: Number(otherPriceCategoryId),
        quantity: 10,
        remainingQuantity: 6,
        activationCodesExpirationDatetime: null,
        isBookable: false,
        dateModified: '2022-05-18T08:25:31.015652Z',
      }),
    ]
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
      stocks: [],
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
    await renderStockEventScreen(apiOffer, apiStocks)

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
    await renderStockEventScreen(apiOffer, apiStocks)
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
    expect(api.deleteStock).toHaveBeenCalledWith(apiStocks[0].id)

    vi.spyOn(api, 'upsertStocks')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should not allow user to delete a stock undeletable', async () => {
    await renderStockEventScreen(apiOffer, [
      { ...apiStocks[0], isEventDeletable: false },
    ])
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    const deleteButton = screen.getAllByTitle('Supprimer le stock')[0]
    expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
    await userEvent.click(deleteButton)
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Tarif')).toHaveValue(otherPriceCategoryId)
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      name: 'Provider',
    }
    await renderStockEventScreen(apiOffer, apiStocks)
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
    expect(api.deleteStock).toHaveBeenCalledWith(apiStocks[0].id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should display new stocks banner when vcreating new stock', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValueOnce({
      stocks: apiStocks,
    })
    await renderStockEventScreen(apiOffer, apiStocks)

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
      stocks: apiStocks,
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
    await renderStockEventScreen(apiOffer, apiStocks)

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
    expect(api.deleteStock).toHaveBeenCalledWith(apiStocks[0].id)
  })

  it('should save the offer without warning on "Enregistrer les modifications" button click', async () => {
    const testedStock = individualGetOfferStockResponseModelFactory({
      bookingsQuantity: 0,
    })

    await renderStockEventScreen(apiOffer, [testedStock])
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [testedStock],
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

  it('should show a warning on click on "Enregistrer les modifications" when stock has already been booked', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValueOnce({ stocks: apiStocks })
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
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a success notification if nothing has been touched', async () => {
    await renderStockEventScreen(apiOffer, apiStocks)

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
    await renderStockEventScreen(apiOffer, apiStocks)

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
    await renderStockEventScreen(apiOffer, apiStocks)

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(
      screen.getByText('This is the read only route content')
    ).toBeInTheDocument()
  })
})
