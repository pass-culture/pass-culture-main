import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { ButtonLink } from 'ui-kit'
import {
  individualOfferContextFactory,
  individualOfferFactory,
  individualOfferVenueFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksThing, { StocksThingProps } from '../StocksThing'

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
    ...((await vi.importActual('utils/date')) ?? {}),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const offerId = 12

const renderStockThingScreen = (
  props: StocksThingProps,
  contextValue: IndividualOfferContextValues,
  url: string = generatePath(
    getIndividualOfferPath({
      step: OFFER_WIZARD_STEP_IDS.STOCKS,
      mode: OFFER_WIZARD_MODE.CREATION,
    }),
    { offerId: offerId }
  )
) =>
  renderWithProviders(
    <Routes>
      {Object.values(OFFER_WIZARD_MODE).map(mode => (
        <Route
          key={mode}
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode,
          })}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <StocksThing {...props} />
              <ButtonLink link={{ to: '/outside', isExternal: false }}>
                Go outside !
              </ButtonLink>
            </IndividualOfferContext.Provider>
          }
        />
      ))}
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>Next page</div>}
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.DRAFT,
        })}
        element={<div>Next page draft</div>}
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>Previous page</div>}
      />
      <Route path="/outside" element={<div>This is outside stock form</div>} />
    </Routes>,
    { initialRouterEntries: [url] }
  )

describe('screens:StocksThing', () => {
  let props: StocksThingProps
  let contextValue: IndividualOfferContextValues
  let offer: IndividualOffer

  beforeEach(() => {
    offer = individualOfferFactory({
      id: offerId,
      venue: individualOfferVenueFactory({
        departmentCode: '75',
      }),
      stocks: [],
    })
    props = {
      offer,
    }
    contextValue = individualOfferContextFactory()
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should not block when going outside and form is not touched', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockThingScreen(props, contextValue)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to stay on stock form after click on "Annuler"', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockThingScreen(props, contextValue)
    await userEvent.type(screen.getByLabelText('Quantité'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Rester sur la page'))

    expect(screen.getByTestId('stock-thing-form')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockThingScreen(props, contextValue)
    await userEvent.type(screen.getByLabelText('Quantité'), '20')

    await userEvent.click(screen.getByText('Go outside !'))
    expect(
      screen.getByText(
        'Restez sur la page et cliquez sur “Sauvegarder le brouillon” pour ne rien perdre de vos modifications.'
      )
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Quitter la page'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(0)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should track when quitting without submit from RouteLeavingGuard', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockThingScreen(props, contextValue)

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Quitter la page'))
  })

  it('should be able to submit from Action Bar without Guard after changing price in draft', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    const stock = individualStockFactory({
      id: 1,
      quantity: 10,
      price: 17.11,
      remainingQuantity: 6,
      bookingsQuantity: 0,
      hasActivationCode: false,
      activationCodesExpirationDatetime: null,
      activationCodes: [],
      beginningDatetime: null,
      bookingLimitDatetime: null,
      isSoftDeleted: false,
      isEventExpired: false,
      isEventDeletable: false,
      dateCreated: new Date(),
    })

    offer = individualOfferFactory({
      id: offerId,
      venue: individualOfferVenueFactory({
        departmentCode: '75',
      }),
      stocks: [stock],
    })

    props.offer = offer
    contextValue.offer = offer
    renderStockThingScreen(
      props,
      contextValue,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      )
    )
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Étape suivante'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)

    expect(screen.getByText('Next page draft')).toBeInTheDocument()
  })
})
