import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOfferStockResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  StocksEventCreationProps,
  StocksEventCreation,
} from '../StocksEventCreation'

vi.mock('apiClient/api', () => ({
  api: {
    getStocks: vi.fn(),
    upsertStocks: vi.fn(),
  },
}))

const renderStockEventCreation = async (
  stocks: GetOfferStockResponseModel[],
  props: StocksEventCreationProps
) => {
  vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
    stocks,
    stockCount: stocks.length,
    hasStocks: stocks.length > 0,
  })
  renderWithProviders(
    <Routes>
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={
          <>
            <StocksEventCreation {...props} />
            <ButtonLink to="/outside">Go outside !</ButtonLink>
            <Notification />
          </>
        }
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={
          <>
            <div>Next page</div>
            <Notification />
          </>
        }
      />
      <Route
        path={getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>Previous page</div>}
      />
      <Route path="/outside" element={<div>This is outside stock form</div>} />
    </Routes>,
    {
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
          offerId: 1,
        }),
      ],
    }
  )
  await waitFor(() => {
    expect(api.getStocks).toHaveBeenCalledTimes(1)
  })
}

const tomorrow = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
describe('StocksEventCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks_count: 0 })
  })

  it('should notify when clicking on Enregistrer et continuer without stock', async () => {
    await renderStockEventCreation([], {
      offer: getIndividualOfferFactory(),
    })
    expect(screen.getByText('Comment faire ?')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()
  })

  it('should not show help section if there are stocks already and show table', async () => {
    await renderStockEventCreation(
      [getOfferStockFactory({ priceCategoryId: 1 })],
      { offer: getIndividualOfferFactory() }
    )

    expect(screen.queryByText('Comment faire ?')).not.toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
  })

  it('should display new stocks banner for several stocks', async () => {
    await renderStockEventCreation([], { offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      tomorrow
    )
    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '12:15')
    await userEvent.click(screen.getByText('12:15'))
    await userEvent.click(screen.getByText('Ajouter un créneau'))
    await userEvent.type(screen.getByLabelText('Horaire 2 *'), '12:30')

    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks_count: 2 })
    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [getOfferStockFactory(), getOfferStockFactory()],
      stockCount: 2,
      hasStocks: true,
    })
    await userEvent.click(screen.getByText('Valider'))
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledTimes(1)
    })

    expect(
      screen.getByText('2 nouvelles dates ont été ajoutées')
    ).toBeInTheDocument()
  })

  it('should redirect to previous page on click to Retour', async () => {
    await renderStockEventCreation([], { offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByText('Retour'))

    expect(screen.getByText('Previous page')).toBeInTheDocument()
  })

  it('should submit and redirect to next page on Enregistrer et continuer click', async () => {
    await renderStockEventCreation([getOfferStockFactory()], {
      offer: getIndividualOfferFactory(),
    })

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(screen.getByText('Next page')).toBeInTheDocument()
  })

  it('should notify when there is not yet stocks', async () => {
    vi.spyOn(api, 'upsertStocks').mockRejectedValueOnce({})

    await renderStockEventCreation([], { offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()

    expect(
      screen.getByText('Ajouter une ou plusieurs dates')
    ).toBeInTheDocument()
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })
})
