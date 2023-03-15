import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import {
  getOfferIndividualPath,
  getOfferIndividualUrl,
} from 'core/Offers/utils/getOfferIndividualUrl'
import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IStocksEventCreationProps,
  StocksEventCreation,
} from '../StocksEventCreation'

const renderStockEventCreation = (props: IStocksEventCreationProps) =>
  renderWithProviders(
    <Routes>
      <Route
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={
          <>
            <StocksEventCreation {...props} />
            <Notification />
          </>
        }
      />
      <Route
        path={getOfferIndividualPath({
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
        path={getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}
        element={<div>Previous page</div>}
      />
    </Routes>,
    {
      initialRouterEntries: [
        getOfferIndividualUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
          offerId: '1',
        }),
      ],
    }
  )

describe('StocksEventCreation', () => {
  it('should show help section if there are not stocks', () => {
    renderWithProviders(
      <StocksEventCreation offer={individualOfferFactory({ stocks: [] })} />
    )

    expect(screen.getByText('Comment faire ?')).toBeInTheDocument()
  })

  it('should not show help section if there are stocks already and show table', () => {
    renderWithProviders(
      <StocksEventCreation
        offer={individualOfferFactory({
          stocks: [individualStockFactory({ priceCategoryId: 1 })],
        })}
      />
    )

    expect(screen.queryByText('Comment faire ?')).not.toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
  })

  it('should open recurrence modal', async () => {
    renderWithProviders(
      <StocksEventCreation
        offer={individualOfferFactory({
          stocks: [individualStockFactory({ priceCategoryId: 1 })],
        })}
      />
    )
    expect(
      screen.queryByRole('heading', { name: 'Ajouter une ou plusieurs dates' })
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))
    expect(
      screen.getByRole('heading', { name: 'Ajouter une ou plusieurs dates' })
    ).toBeInTheDocument()
  })
})

describe('navigation and submit', () => {
  beforeEach(() => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })

  it('should redirect to previous page on click to Étape précédente', async () => {
    renderStockEventCreation({ offer: individualOfferFactory({ stocks: [] }) })

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(screen.getByText('Previous page')).toBeInTheDocument()
  })

  it('should submit and redirect to next page on clik to Étape suivante', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [individualStockFactory({ id: undefined, priceCategoryId: 1 })],
      }),
    })

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(screen.getByText('Next page')).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should submit and stay to stocks page on clik to Sauvegarder le brouillon', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [individualStockFactory({ id: undefined, priceCategoryId: 1 })],
      }),
    })

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Ajouter une ou plusieurs dates')
    ).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })

  it('should notify when an error occur', async () => {
    jest.spyOn(api, 'upsertStocks').mockRejectedValue({})

    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [individualStockFactory({ id: undefined, priceCategoryId: 1 })],
      }),
    })

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      screen.getByText(
        "Une erreur est survenue lors de l'enregistrement de vos stocks."
      )
    ).toBeInTheDocument()

    expect(
      screen.getByText('Ajouter une ou plusieurs dates')
    ).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
  })
})

describe('deletion', () => {
  beforeEach(() => {
    jest.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })
    jest.spyOn(api, 'deleteStock').mockResolvedValue({ id: 'AA' })
    jest
      .spyOn(api, 'getOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)
  })

  it('should delete new stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [],
      }),
    })

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.click(
      screen.getByLabelText('Date de l’évènement', { exact: true })
    )
    await userEvent.click(screen.getByText(new Date().getDate()))
    await userEvent.click(screen.getByLabelText('Horaire 1'))
    await userEvent.click(screen.getByText('12:00'))
    await userEvent.click(screen.getByText('Ajouter cette date'))
    // stock line are here
    expect(screen.queryByText('Date')).toBeInTheDocument()

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le stock' })[0]
    )

    // stock line is not here anymore
    expect(screen.queryByText('Date')).not.toBeInTheDocument()
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledTimes(0)
  })

  it('should delete already created stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [individualStockFactory({ id: 'AA', priceCategoryId: 1 })],
      }),
    })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le stock' })[0]
    )
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
  })
})
