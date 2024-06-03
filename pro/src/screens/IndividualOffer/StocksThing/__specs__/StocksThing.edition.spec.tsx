import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
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
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { Stocks } from 'pages/IndividualOfferWizard/Stocks/Stocks'
import { getOfferStockFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

vi.mock('screens/IndividualOffer/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

vi.mock('utils/date', async () => {
  return {
    ...(await vi.importActual('utils/date')),
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
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
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
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
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
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
          offerId: 12,
        }),
      ],
    }
  )

describe('screens:StocksThing', () => {
  let apiOffer: GetIndividualOfferResponseModel
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
    apiOffer = {
      bookingEmail: null,
      dateCreated: '2022-05-18T08:25:30.991476Z',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      extraData: null,
      hasBookingLimitDatetimesPassed: true,
      hasStocks: true,
      isActive: true,
      isActivable: true,
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
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      thumbUrl: null,
      externalTicketOfficeUrl: null,
      url: null,
      venue: {
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
        street: '1 boulevard Poissonnière',
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
    }

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
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks_count: 0 })
  })

  it('should allow user to delete a stock', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')
    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    await userEvent.click(await screen.findByText('Supprimer le stock'))
    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Supprimer', { selector: 'button' }))
    expect(
      await screen.findByText('Le stock a été supprimé.')
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByLabelText('Prix *')).toHaveValue(null)
    })
    expect(api.deleteStock).toHaveBeenCalledWith(stockToDelete.id)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(
      await screen.findByText('This is the read only route content')
    ).toBeInTheDocument()
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should allow user to delete stock from a synchronized offer', async () => {
    apiOffer.lastProvider = {
      name: 'Provider',
    }
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[1])
    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[0])
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
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
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
    renderStockThingScreen()
    await screen.findByTestId('stock-thing-form')

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
    expect(screen.queryByTestId('stock-thing-form')).not.toBeInTheDocument()
    expect(
      screen.getByText(/This is the read only route content/)
    ).toBeInTheDocument()
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
    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    await userEvent.click(await screen.findByTitle('Supprimer le stock'))
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
