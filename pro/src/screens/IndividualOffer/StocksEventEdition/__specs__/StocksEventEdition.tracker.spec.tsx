import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import format from 'date-fns/format'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { IndividualOffer, IndividualOfferVenue } from 'core/Offers/types'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksEventEdition, {
  StocksEventEditionProps,
} from '../StocksEventEdition'

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
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockEventScreen = (
  props: StocksEventEditionProps,
  contextValue: IndividualOfferContextValues,
  url = '/creation/stocks'
) =>
  renderWithProviders(
    <>
      <Routes>
        {['/creation/stocks', '/brouillon/stocks', '/stocks'].map(path => (
          <Route
            key={path}
            path={path}
            element={
              <IndividualOfferContext.Provider value={contextValue}>
                <StocksEventEdition {...props} />
              </IndividualOfferContext.Provider>
            }
          />
        ))}
      </Routes>
      <Notification />
    </>,
    { initialRouterEntries: [url] }
  )

const priceCategoryId = '1'

describe('screens:StocksEventEdition', () => {
  let props: StocksEventEditionProps
  let contextValue: IndividualOfferContextValues
  let offer: Partial<IndividualOffer>
  const offerId = 12

  beforeEach(() => {
    offer = {
      id: offerId,
      venue: {
        departmentCode: '75',
      } as IndividualOfferVenue,
      stocks: [],
      priceCategories: [
        { id: Number(priceCategoryId), label: 'Cat 1', price: 10 },
        { id: 2, label: 'Cat 2', price: 20 },
      ],
    }
    props = {
      offer: offer as IndividualOffer,
    }
    contextValue = {
      offerId: null,
      offer: null,
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
  })

  it('should track when clicking on "Enregistrer les modifications" on edition', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockEventScreen(props, contextValue, '/stocks')

    await userEvent.type(
      screen.getByLabelText('Date'),
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire'), '12:00')
    await userEvent.selectOptions(
      screen.getByLabelText('Tarif'),
      priceCategoryId
    )
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
  })
})
