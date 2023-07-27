import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import {
  OfferIndividualContextValues,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OfferIndividual, OfferIndividualVenue } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksThing, { StocksThingProps } from '../StocksThing'

const mockLogEvent = vi.fn()

vi.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

vi.mock('utils/date', () => ({
  ...vi.importActual('utils/date'),
  getToday: vi.fn().mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderStockThingScreen = (
  props: StocksThingProps,
  contextValue: OfferIndividualContextValues,
  url = '/creation/stocks'
) =>
  renderWithProviders(
    <Routes>
      {['/creation/stocks', '/brouillon/stocks', '/stocks'].map(path => (
        <Route
          key={path}
          path={path}
          element={
            <OfferIndividualContext.Provider value={contextValue}>
              <StocksThing {...props} />
            </OfferIndividualContext.Provider>
          }
        />
      ))}
    </Routes>,
    { initialRouterEntries: [url] }
  )

describe('screens:StocksThing', () => {
  let props: StocksThingProps
  let contextValue: OfferIndividualContextValues
  let offer: Partial<OfferIndividual>
  const offerId = 1

  beforeEach(() => {
    offer = {
      id: offerId,
      venue: {
        departmentCode: '75',
      } as OfferIndividualVenue,
      stocks: [],
    }
    props = {
      offer: offer as OfferIndividual,
    }
    contextValue = {
      offerId: null,
      offer: null,
      venueList: [],
      offererNames: [],
      categories: [],
      subCategories: [],
      setOffer: () => {},
      setShouldTrack: () => {},
      shouldTrack: true,
      showVenuePopin: {},
    }
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should track when clicking on "Sauvegarder le brouillon" on creation', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockThingScreen(props, contextValue)

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'stocks',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when clicking on "Sauvegarder le brouillon" on draft', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockThingScreen(props, contextValue, '/brouillon/stocks')

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'stocks',
        used: 'DraftButtons',
      }
    )
  })

  it('should track when clicking on "Étape suivante" on creation', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockThingScreen(props, contextValue)

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape suivante" on brouillon', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockThingScreen(props, contextValue, '/brouillon/stocks')

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Enregistrer les modifications" on edition', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })
    renderStockThingScreen(props, contextValue, '/stocks')

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape précédente" on creation', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockThingScreen(props, contextValue)

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Étape précédente" on draft', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockThingScreen(props, contextValue, '/brouillon/stocks')

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: offerId,
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when clicking on "Annuler et quitter" on edition', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 1 } as StockResponseModel],
    })

    renderStockThingScreen(props, contextValue, '/stocks')

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: offerId,
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
  })
})
