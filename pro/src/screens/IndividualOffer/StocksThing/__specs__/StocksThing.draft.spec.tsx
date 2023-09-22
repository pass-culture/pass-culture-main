import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  IndividualOffer,
  IndividualOfferStock,
  IndividualOfferVenue,
} from 'core/Offers/types'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
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

const renderStockThingScreen = (
  props: StocksThingProps,
  contextValue: IndividualOfferContextValues
) =>
  renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <StocksThing {...props} />
            </IndividualOfferContext.Provider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.DRAFT,
          })}
          element={<div>Next page</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.DRAFT,
          offerId: contextValue.offer?.id || undefined,
        }),
      ],
    }
  )

describe('screens:StocksThing::draft', () => {
  let props: StocksThingProps
  let contextValue: IndividualOfferContextValues
  let offer: Partial<IndividualOffer>
  let stock: Partial<IndividualOfferStock>
  const offerId = 1

  beforeEach(() => {
    stock = {
      id: 1,
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 4,
      isEventDeletable: true,
    }
    offer = {
      id: 1,
      lastProvider: null,
      venue: {
        departmentCode: '75',
      } as IndividualOfferVenue,
      stocks: [stock as IndividualOfferStock],
    }
    props = {
      offer: offer as IndividualOffer,
    }
    contextValue = {
      offerId: offerId,
      offer: offer as IndividualOffer,
      venueList: [],
      offererNames: [],
      categories: [],
      subCategories: [],
      setOffer: () => {},
      setSubcategory: () => {},
      showVenuePopin: {},
    }
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'upsertStocks')
  })

  it('should show a success notification if nothing has been touched', async () => {
    renderStockThingScreen(props, contextValue)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Sauvegarder le brouillon',
      })
    )

    expect(api.upsertStocks).not.toHaveBeenCalled()
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByTestId('stock-thing-form')).toBeInTheDocument()
    expect(screen.queryByText(/Next page/)).not.toBeInTheDocument()
  })
})
