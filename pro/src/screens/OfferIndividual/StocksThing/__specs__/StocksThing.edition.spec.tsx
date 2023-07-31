import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

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
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  getOfferIndividualPath,
  getOfferIndividualUrl,
} from 'core/Offers/utils/getOfferIndividualUrl'
import Stocks from 'pages/OfferIndividualWizard/Stocks/Stocks'
import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

vi.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

vi.mock('utils/date', async () => {
  const actual = (await vi.importActual('utils/date')) || {}
  return {
    ...actual,
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockThingScreen = (storeOverrides: Partial<RootState> = {}) =>
  renderWithProviders(
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
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
          element={<div>Save draft page</div>}
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

describe('screens:StocksThing', () => {
  let storeOverride: Partial<RootState>
  let apiOffer: GetIndividualOfferResponseModel
  const stockToDelete = {
    beginningDatetime: '2022-05-23T08:25:31.009799Z',
    bookingLimitDatetime: '2022-05-23T07:25:31.009799Z',
    bookingsQuantity: 4,
    dateCreated: '2022-05-18T08:25:31.015652Z',
    hasActivationCode: false,
    id: 1,
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
      isDigital: false,
      isDuo: false,
      isEditable: true,
      isEvent: false,
      isNational: false,
      isThing: false,
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      id: 12,
      visualDisabilityCompliant: false,
      lastProvider: null,
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
    storeOverride = {
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

    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'listOffers').mockResolvedValue([
      {
        id: 1,
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
          id: 1,
        },
        stocks: [],
        isEditable: true,
        isShowcase: false,
        isThing: false,
        subcategoryId: SubcategoryIdEnum.VOD,
      },
    ])
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })
  })

  it.skip('should allow user to delete a stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen(storeOverride)
    await screen.findByTestId('stock-thing-form')

    // userEvent.dblClick to fix @reach/menu-button update, to delete after refactor
    await userEvent.dblClick(screen.getByText('Supprimer le stock'))
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()

    apiOffer.stocks = []
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByLabelText('Prix')).toHaveValue(null)
    })
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      name: 'Provider',
    }
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen(storeOverride)
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[1]
    )
    await userEvent.click(
      screen.getAllByTestId('stock-form-actions-button-open')[0]
    )
    await userEvent.dblClick(screen.getAllByText('Supprimer le stock')[0])
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
    renderStockThingScreen(storeOverride)
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(screen.getByTestId('stock-form-actions-button-open'))
    await userEvent.dblClick(screen.getByText('Supprimer le stock'))
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
    renderStockThingScreen(storeOverride)
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('stock-thing-form')).not.toBeInTheDocument()

    expect(screen.getByText(/Next page/)).toBeInTheDocument()
  })

  it('should not display any message when user delete empty stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen(storeOverride)
    apiOffer.stocks = []
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    await screen.findByTestId('stock-thing-form')
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
  it('should display draft success message on save button when stock form is empty and redirect to next page', async () => {
    renderStockThingScreen(storeOverride)
    apiOffer.stocks = []
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      screen.getByText('Vos modifications ont bien été enregistrées')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('stock-thing-form')).not.toBeInTheDocument()
    expect(screen.getByText(/Next page/)).toBeInTheDocument()
  })
})
