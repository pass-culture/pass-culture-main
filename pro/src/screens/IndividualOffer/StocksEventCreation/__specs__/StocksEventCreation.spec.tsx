import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays } from 'date-fns'
import format from 'date-fns/format'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
import { ButtonLink } from 'ui-kit'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import {
  individualOfferFactory,
  individualStockEventFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  StocksEventCreationProps,
  StocksEventCreation,
} from '../StocksEventCreation'

const renderStockEventCreation = (props: StocksEventCreationProps) =>
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
            <ButtonLink link={{ to: '/outside', isExternal: false }}>
              Go outside !
            </ButtonLink>
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

const tomorrow = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
describe('StocksEventCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })
  })

  it('should show help section if there are not stocks', () => {
    renderStockEventCreation({
      offer: individualOfferFactory({ stocks: [] }),
      stocks: [],
      setStocks: vi.fn(),
    })

    expect(screen.getByText('Comment faire ?')).toBeInTheDocument()
  })

  it('should notify when clicking on Enregistrer et continuer without stock', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({ stocks: [] }),
      stocks: [],
      setStocks: vi.fn(),
    })

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()
  })

  it('should not show help section if there are stocks already and show table', () => {
    renderStockEventCreation({
      offer: individualOfferFactory(),
      stocks: [individualStockEventFactory({ priceCategoryId: 1 })],
      setStocks: vi.fn(),
    })

    expect(screen.queryByText('Comment faire ?')).not.toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
  })

  it('should paginate stocks', async () => {
    const stocks = []
    for (let i = 0; i < 30; i++) {
      stocks.push(individualStockEventFactory({ priceCategoryId: 1 }))
    }

    renderStockEventCreation({
      offer: individualOfferFactory(),
      stocks,
      setStocks: vi.fn(),
    })

    expect(screen.queryAllByRole('button', { name: 'Supprimer' })).toHaveLength(
      20
    )
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    expect(screen.queryAllByRole('button', { name: 'Supprimer' })).toHaveLength(
      10
    )
  })

  it('should open recurrence modal', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory(),
      stocks: [individualStockEventFactory({ priceCategoryId: 1 })],
      setStocks: vi.fn(),
    })
    expect(
      screen.queryByRole('heading', { name: 'Ajouter une ou plusieurs dates' })
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))
    expect(
      screen.getByRole('heading', { name: 'Ajouter une ou plusieurs dates' })
    ).toBeInTheDocument()
  })

  it('should display new stocks banner for several stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory(),
      stocks: [],
      setStocks: vi.fn(),
    })

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.type(screen.getByLabelText('Date de l’évènement'), tomorrow)
    await userEvent.type(screen.getByLabelText('Horaire 1'), '12:15')
    await userEvent.click(screen.getByText('12:15'))
    await userEvent.click(screen.getByText('Ajouter un créneau'))
    await userEvent.type(screen.getByLabelText('Horaire 2'), '12:30')
    await userEvent.click(screen.getByText('Valider'))

    expect(
      screen.getByText('2 nouvelles occurrences ont été ajoutées')
    ).toBeInTheDocument()
  })

  it('should redirect to previous page on click to Retour', async () => {
    const offer = individualOfferFactory()
    renderStockEventCreation({
      offer,
      stocks: [],
      setStocks: vi.fn(),
    })

    await userEvent.click(screen.getByText('Retour'))

    expect(screen.getByText('Previous page')).toBeInTheDocument()
  })

  it('should submit and redirect to next page on Enregistrer et continuer click', async () => {
    const offer = individualOfferFactory()
    renderStockEventCreation({
      offer,
      stocks: [
        individualStockEventFactory({
          id: undefined,
          priceCategoryId: 1,
        }),
      ],
      setStocks: vi.fn(),
    })

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(screen.getByText('Next page')).toBeInTheDocument()
  })

  it('should redirect to previous page on Retour click', async () => {
    const offer = individualOfferFactory()
    renderStockEventCreation({
      offer,
      stocks: [],
      setStocks: vi.fn(),
    })

    await userEvent.click(screen.getByText('Retour'))

    expect(screen.getByText('Previous page')).toBeInTheDocument()
  })

  it('should notify when there is not yet stocks', async () => {
    vi.spyOn(api, 'upsertStocks').mockRejectedValueOnce({})

    const offer = individualOfferFactory()

    renderStockEventCreation({
      offer,
      stocks: [],
      setStocks: vi.fn(),
    })

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()

    expect(
      screen.getByText('Ajouter une ou plusieurs dates')
    ).toBeInTheDocument()
    expect(api.upsertStocks).not.toHaveBeenCalled()
  })

  it('should delete  stocks', async () => {
    vi.spyOn(api, 'deleteStock').mockResolvedValueOnce({ id: 1 })

    renderStockEventCreation({
      offer: individualOfferFactory(),
      stocks: [individualStockEventFactory({ id: 12, priceCategoryId: 1 })],
      setStocks: vi.fn(),
    })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )
    await userEvent.click(screen.getByText('Enregistrer et continuer'))
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
  })
})
