import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  OfferStatus,
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
import Stocks from 'pages/OfferIndividualWizard/Stocks/Stocks'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

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

const renderStockThingScreen = ({
  offerId = 'OFFER_ID',
  storeOverride = {},
}: {
  offerId?: string
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
            offerId: offerId || undefined,
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
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
        >
          <div>Save draft page</div>
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

describe('screens:StocksThing', () => {
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
      isEvent: false,
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
          beginningDatetime: '2022-05-23T08:25:31.009799Z',
          bookingLimitDatetime: '2022-05-23T07:25:31.009799Z',
          bookingsQuantity: 4,
          dateCreated: '2022-05-18T08:25:31.015652Z',
          hasActivationCode: false,
          id: 'STOCK_ID',
          isEventDeletable: false,
          isEventExpired: true,
          isSoftDeleted: false,
          offerId: 'YA',
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
    renderStockThingScreen({
      storeOverride,
    })
    await screen.findByRole('heading', { name: /Stock & Prix/ })
    await userEvent.click(screen.getAllByTitle('Supprimer le stock')[1])
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()

    apiOffer.stocks = []
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(screen.getByText('Le stock a été supprimé.')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByLabelText('Prix')).toHaveValue(null)
    })
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
    expect(api.deleteStock).toHaveBeenCalledTimes(1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    jest.spyOn(api, 'upsertStocks')
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })
  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      id: 'PROVIDER_ID',
      isActive: true,
      name: 'Provider',
      enabledForPro: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'OFFER_ID' })
    renderStockThingScreen({
      storeOverride,
    })
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
    renderStockThingScreen({
      storeOverride,
    })
    await screen.findByRole('heading', { name: /Stock & Prix/ })

    await userEvent.click(screen.getByTestId('stock-form-actions-button-open'))
    await userEvent.click(screen.getByText('Supprimer le stock'))
    await userEvent.click(
      await screen.findByText('Supprimer', { selector: 'button' })
    )
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledWith('STOCK_ID')
    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression du stock.'
      )
    ).toBeInTheDocument()
  })
  it('should show a success notification if nothing has been touched', async () => {
    renderStockThingScreen({ storeOverride })
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
