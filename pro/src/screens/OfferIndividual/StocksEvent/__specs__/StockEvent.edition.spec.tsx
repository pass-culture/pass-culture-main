import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  OfferStatus,
  StockResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import {
  getOfferIndividualPath,
  getOfferIndividualUrl,
} from 'core/Offers/utils/getOfferIndividualUrl'
import { Stocks } from 'pages/OfferIndividualWizard/Stocks'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderStockEventScreen = ({
  storeOverride = {},
}: {
  storeOverride: Partial<RootState>
}) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          getOfferIndividualUrl({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
            offerId: 'OFFER_ID',
          }),
        ]}
      >
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
        >
          <OfferIndividualContextProvider
            isUserAdmin={false}
            offerId="OFFER_ID"
          >
            <Stocks />
          </OfferIndividualContextProvider>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
        >
          <div>Next page</div>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
        >
          <div>Previous page</div>
        </Route>
        <Notification />
      </MemoryRouter>
    </Provider>
  )
}

describe('screens:StocksEvent:Edition', () => {
  let storeOverride: Partial<RootState>
  let apiOffer: GetIndividualOfferResponseModel

  beforeEach(() => {
    apiOffer = {
      activeMediation: null,
      ageMax: null,
      ageMin: null,
      bookingEmail: null,
      conditions: null,
      dateCreated: '2022-05-18T08:25:30.991476Z',
      dateModifiedAtLastProvider: '2022-05-18T08:25:30.991481Z',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      extraData: null,
      fieldsUpdated: [],
      hasBookingLimitDatetimesPassed: true,
      id: 'OFFER_ID',
      isActive: true,
      isBookable: false,
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
      nonHumanizedId: 192,
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
      product: {
        ageMax: null,
        ageMin: null,
        conditions: null,
        dateModifiedAtLastProvider: '2022-05-18T08:25:30.980975Z',
        description: 'A passionate description of product 80',
        durationMinutes: null,
        extraData: null,
        fieldsUpdated: [],
        id: 'AJFA',
        idAtProviders: null,
        isGcuCompatible: true,
        isNational: false,
        lastProviderId: null,
        mediaUrls: [],
        name: 'Product 80',
        owningOffererId: null,
        thumbCount: 0,
        url: null,
      },
      productId: 'AJFA',
      stocks: [
        {
          beginningDatetime: '2023-01-23T08:25:31.009799Z',
          bookingLimitDatetime: '2023-01-23T07:25:31.009799Z',
          bookingsQuantity: 4,
          dateCreated: '2022-05-18T08:25:31.015652Z',
          hasActivationCode: false,
          id: 'STOCK_ID',
          isEventDeletable: true,
          isEventExpired: false,
          isSoftDeleted: false,
          offerId: 'OFFER_ID',
          price: 10.01,
          quantity: 10,
          remainingQuantity: 6,
          activationCodesExpirationDatetime: null,
          isBookable: false,
          dateModified: '2022-05-18T08:25:31.015652Z',
          fieldsUpdated: [],
        },
      ],
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      thumbUrl: null,
      externalTicketOfficeUrl: null,
      url: null,
      venue: {
        address: '1 boulevard Poissonnière',
        bookingEmail: 'venue29@example.net',
        city: 'Paris',
        comment: null,
        dateCreated: '2022-05-18T08:25:30.929961Z',
        dateModifiedAtLastProvider: '2022-05-18T08:25:30.929955Z',
        departementCode: '75',
        fieldsUpdated: [],
        id: 'DY',
        idAtProviders: null,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.87004,
        longitude: 2.3785,
        managingOfferer: {
          address: '1 boulevard Poissonnière',
          city: 'Paris',
          dateCreated: '2022-05-18T08:25:30.891369Z',
          dateModifiedAtLastProvider: '2022-05-18T08:25:30.891364Z',
          fieldsUpdated: [],
          id: 'CU',
          idAtProviders: null,
          isActive: true,
          isValidated: true,
          lastProviderId: null,
          name: 'Le Petit Rintintin Management 6',
          postalCode: '75000',
          siren: '000000006',
          thumbCount: 0,
        },
        managingOffererId: 'CU',
        name: 'Cinéma synchro avec booking provider',
        postalCode: '75000',
        publicName: 'Cinéma synchro avec booking provider',
        siret: '00000000600029',
        thumbCount: 0,
        venueLabelId: null,
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
      },
      venueId: 'DY',
      withdrawalDetails: null,
      status: OfferStatus.EXPIRED,
      withdrawalType: null,
      withdrawalDelay: null,
    }
    storeOverride = {
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
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: [] })
    jest.spyOn(api, 'upsertStocks')
    jest.spyOn(api, 'listOffers').mockResolvedValue([
      {
        id: 'id',
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

  it('should allow user to delete a stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    apiOffer.stocks = [
      ...apiOffer.stocks,
      {
        beginningDatetime: '2023-01-20T08:25:31.009799Z',
        bookingLimitDatetime: '2023-01-20T07:25:31.009799Z',
        bookingsQuantity: 5,
        dateCreated: '2022-05-18T08:25:31.015652Z',
        hasActivationCode: false,
        id: 'STOCK_ID_2',
        isEventDeletable: true,
        isEventExpired: false,
        isSoftDeleted: false,
        offerId: 'OFFER_ID',
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
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    await userEvent.click(screen.getAllByText('Supprimer le stock')[0])
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(screen.getByText('Le stock a été supprimé.')).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    jest.spyOn(api, 'upsertStocks')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it("should allow user to delete a stock he just created (and didn't save)", async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.click(await screen.findByText('Ajouter une date'))
    await userEvent.type(screen.getAllByLabelText('Prix')[0], '20')
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    await userEvent.click(screen.getAllByText('Supprimer le stock')[0])

    expect(api.deleteStock).toHaveBeenCalledTimes(0)
    expect(screen.getAllByLabelText('Prix').length).toBe(1)
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should keep user modifications when deleting a exiting stock', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    const previousApiOffer = { ...apiOffer }
    apiOffer.stocks = [
      ...apiOffer.stocks,
      {
        beginningDatetime: '2023-01-20T08:25:31.009799Z',
        bookingLimitDatetime: '2023-01-20T07:25:31.009799Z',
        bookingsQuantity: 5,
        dateCreated: '2022-05-18T08:25:31.015652Z',
        hasActivationCode: false,
        id: 'STOCK_ID_2',
        isEventDeletable: true,
        isEventExpired: false,
        isSoftDeleted: false,
        offerId: 'OFFER_ID',
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

    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    // create new stock
    await userEvent.click(await screen.findByText('Ajouter une date'))
    await userEvent.type(screen.getAllByLabelText('Prix')[0], '20')

    // delete existing stock
    jest.spyOn(api, 'getOffer').mockResolvedValue(previousApiOffer)
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[2]
    )
    await userEvent.click(screen.getAllByText('Supprimer le stock')[2])
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(screen.getByText('Le stock a été supprimé.')).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID_2')
    expect(api.deleteStock).toHaveBeenCalledTimes(1)

    const allPriceInputs = screen.getAllByLabelText('Prix')
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
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    apiOffer.stocks = [
      {
        ...apiOffer.stocks[0],
        isEventDeletable: false,
      },
    ]
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    const deleteButton = screen.getAllByTitle('Supprimer le stock')[0]
    expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
    await deleteButton.click()
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Prix')).toHaveValue(10.01)
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      id: 'PROVIDER_ID',
      isActive: true,
      name: 'Provider',
      enabledForPro: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    await userEvent.click(screen.getAllByText('Supprimer le stock')[0])
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(screen.getByText('Le stock a été supprimé.')).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })

  it('should not allow user to add a date for a synchronized offer', async () => {
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    apiOffer.lastProvider = {
      ...apiOffer.lastProvider,
      id: 'PROVIDER_ID',
      isActive: true,
      name: 'Provider',
      enabledForPro: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    expect(screen.queryByText('Ajouter une date')).toBeDisabled()
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
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.click(screen.getByTestId('stock-form-actions-button-open'))
    await userEvent.click(screen.getByText('Supprimer le stock'))
    await userEvent.click(
      await screen.findByText('Supprimer', { selector: 'button' })
    )
    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression du stock.'
      )
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
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
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.type(screen.getByLabelText('Prix'), '20')
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
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      await screen.getByText('Des réservations sont en cours pour cette offre')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Confirmer les modifications'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should show a success notification if nothing has been touched', async () => {
    renderStockEventScreen({ storeOverride })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: /Stock & Prix/ })
    ).not.toBeInTheDocument()
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
  })
})
