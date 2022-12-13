import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { generatePath, MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  StockResponseModel,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { ButtonLink } from 'ui-kit'
import { getToday } from 'utils/date'

import StocksEvent, { IStocksEventProps } from '../StocksEvent'

const mockLogEvent = jest.fn()

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

const renderStockEventScreen = ({
  props,
  storeOverride = {},
  contextValue,
  url = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.CREATION,
  }),
}: {
  props: IStocksEventProps
  storeOverride: Partial<RootState>
  contextValue: IOfferIndividualContext
  url?: string
}) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route
          path={Object.values(OFFER_WIZARD_MODE).map(mode =>
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode,
            })
          )}
        >
          <OfferIndividualContext.Provider value={contextValue}>
            <StocksEvent {...props} />
            <ButtonLink link={{ to: '/outside', isExternal: false }}>
              Go outside !
            </ButtonLink>
          </OfferIndividualContext.Provider>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
        >
          <div>Next page</div>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
        >
          <div>Save draft page</div>
        </Route>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
        >
          <div>Previous page</div>
        </Route>
        <Route path="/outside">
          <div>This is outside stock form</div>
        </Route>
        <Notification />
      </MemoryRouter>
    </Provider>
  )
}

const today = getToday()

describe('screens:StocksEvent', () => {
  let props: IStocksEventProps
  let storeOverride: Partial<RootState>
  let contextValue: IOfferIndividualContext
  let offer: Partial<IOfferIndividual>

  beforeEach(() => {
    offer = {
      id: 'OFFER_ID',
      venue: {
        departmentCode: '75',
      } as IOfferIndividualVenue,
      stocks: [],
    }
    props = {
      offer: offer as IOfferIndividual,
    }
    storeOverride = {}
    contextValue = {
      offerId: null,
      offer: null,
      venueList: [],
      offererNames: [],
      categories: [],
      subCategories: [],
      setOffer: () => {},
      setShouldTrack: () => {},
      shouldTrack: false,
      isFirstOffer: false,
      setVenueId: () => {},
    }
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should not block when submitting stock when clicking on "Sauvegarder le brouillon"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Sauvegarder le brouillon' })
    )
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Save draft page')).toBeInTheDocument()
  })

  it('should not block and submit stock form when click on "Étape suivante"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })
    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Next page')).toBeInTheDocument()
  })

  it('should not block when going outside and form is not touched', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should block when clicking on "Étape précédente"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape précédente' })
    )
    await userEvent.click(screen.getByText('Ne pas enregistrer'))

    expect(await screen.findByText('Previous page')).toBeInTheDocument()
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should be able to stay on stock form after click on "Annuler"', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Rester sur cette page'))

    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Poursuivre la navigation'))

    expect(api.upsertStocks).toHaveBeenCalledTimes(0)
    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should track when quitting without submit from RouteLeavingGuard', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({ props, storeOverride, contextValue })

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Quitter sans enregistrer'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: 'OFFER_ID',
        to: '/outside',
        used: 'RouteLeavingGuard',
      }
    )
  })

  it('should be able to submit from RouteLeavingGuard in creation', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
    })
    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées dans votre brouillon.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to submit from RouteLeavingGuard in draft', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      ),
    })
    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées dans votre brouillon.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should track when submitting from RouteLeavingGuard in draft', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      ),
    })
    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: true,
        offerId: 'OFFER_ID',
        to: '/outside',
        used: 'RouteLeavingGuard',
      }
    )
  })

  it('should be able to submit from RouteLeavingGuard in edition', async () => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [{ id: 'CREATED_STOCK_ID' } as StockResponseModel],
    })

    renderStockEventScreen({
      props,
      storeOverride,
      contextValue,
      url: generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: 'AA' }
      ),
    })
    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(await screen.getByText(today.getDate()))
    await userEvent.click(screen.getByLabelText('Horaire'))
    await userEvent.click(await screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Prix'), '20')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Si vous quittez, les informations saisies ne seront pas sauvegardées.'
      )
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getAllByText('Enregistrer les modifications')[1]
    )
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })
})
