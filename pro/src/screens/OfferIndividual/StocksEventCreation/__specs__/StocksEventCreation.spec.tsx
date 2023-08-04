import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import format from 'date-fns/format'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { OfferIndividualStock } from 'core/Offers/types'
import {
  getOfferIndividualPath,
  getOfferIndividualUrl,
} from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import {
  individualOfferFactory,
  individualStockFactory,
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
        path={getOfferIndividualPath({
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
      <Route path="/outside" element={<div>This is outside stock form</div>} />
    </Routes>,
    {
      initialRouterEntries: [
        getOfferIndividualUrl({
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
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should show help section if there are not stocks', () => {
    renderWithProviders(
      <StocksEventCreation offer={individualOfferFactory({ stocks: [] })} />
    )

    expect(screen.getByText('Comment faire ?')).toBeInTheDocument()
  })

  it('should notify when clicking on Étape suivante without stock', async () => {
    renderStockEventCreation({ offer: individualOfferFactory({ stocks: [] }) })

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()
  })

  it('should notify when clicking on Sauvegarder le brouillon without stock', async () => {
    renderStockEventCreation({ offer: individualOfferFactory({ stocks: [] }) })

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      screen.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
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

  it('should paginate stocks', async () => {
    const stocks: OfferIndividualStock[] = []
    for (let i = 0; i < 30; i++) {
      stocks.push(individualStockFactory({ priceCategoryId: 1 }))
    }

    renderWithProviders(
      <StocksEventCreation offer={individualOfferFactory({ stocks })} />
    )

    expect(screen.queryAllByRole('button', { name: 'Supprimer' })).toHaveLength(
      20
    )
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    expect(screen.queryAllByRole('button', { name: 'Supprimer' })).toHaveLength(
      10
    )
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

  it('should display new stocks banner for several stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [],
      }),
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

  it('should deduplicate stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [],
      }),
    })

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))
    await userEvent.type(screen.getByLabelText('Date de l’évènement'), tomorrow)
    await userEvent.type(screen.getByLabelText('Horaire 1'), '12:15')
    await userEvent.click(screen.getByText('Valider'))

    expect(
      screen.getByText('1 nouvelle occurrence a été ajoutée')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))
    await userEvent.type(
      screen.getByLabelText('Date de l’évènement'),
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire 1'), '12:15')
    await userEvent.click(screen.getByText('Valider'))

    // Only one line was created
    expect(screen.queryAllByText('Illimité')).toHaveLength(1)
  })
})

const mockLogEvent = vi.fn()
describe('navigation and submit', () => {
  beforeEach(() => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should redirect to previous page on click to Étape précédente', async () => {
    const offer = individualOfferFactory({
      stocks: [],
    })
    renderStockEventCreation({ offer })

    await userEvent.click(screen.getByText('Étape précédente'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offer.id,
        to: 'tarifs',
        used: 'StickyButtons',
      }
    )
    expect(screen.getByText('Previous page')).toBeInTheDocument()
  })

  it('should submit and redirect to next page on Étape suivante click', async () => {
    const offer = individualOfferFactory({
      stocks: [
        individualStockFactory({
          id: undefined,
          priceCategoryId: 1,
        }),
      ],
    })
    renderStockEventCreation({ offer })

    await userEvent.click(screen.getByText('Étape suivante'))

    await waitFor(() => {
      expect(screen.getByText('Next page')).toBeInTheDocument()
    })
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offer.id,
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should submit and stay on stocks page on Sauvegarder le brouillon click', async () => {
    const offer = individualOfferFactory({
      stocks: [
        individualStockFactory({
          id: undefined,
          priceCategoryId: 1,
        }),
      ],
    })
    renderStockEventCreation({ offer })

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Ajouter une ou plusieurs dates')
    ).toBeInTheDocument()
    expect(api.upsertStocks).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offer.id,
        to: 'stocks',
        used: 'DraftButtons',
      }
    )
  })

  it('should notify when an error occur', async () => {
    vi.spyOn(api, 'upsertStocks').mockRejectedValue({})

    const offer = individualOfferFactory({
      stocks: [
        individualStockFactory({
          id: undefined,
          priceCategoryId: 1,
        }),
      ],
    })
    renderStockEventCreation({ offer })

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
    expect(mockLogEvent).toHaveBeenCalledTimes(0)
  })

  it('should track when quitting without submit from RouteLeavingGuard', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })

    const offer = individualOfferFactory({
      stocks: [
        individualStockFactory({
          id: undefined,
          priceCategoryId: 1,
        }),
      ],
    })
    renderStockEventCreation({
      offer,
    })

    await userEvent.click(screen.getByText('Go outside !'))
    expect(api.upsertStocks).not.toHaveBeenCalled()

    await userEvent.click(screen.getByText('Quitter la page'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: true,
        isEdition: false,
        offerId: offer.id,
        to: '/outside',
        used: 'RouteLeavingGuard',
      }
    )
  })
})

describe('deletion', () => {
  beforeEach(() => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({ stocks: [] })
    vi.spyOn(api, 'deleteStock').mockResolvedValue({ id: 1 })
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should delete new stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [],
      }),
    })

    await userEvent.click(screen.getByText('Ajouter une ou plusieurs dates'))

    await userEvent.type(screen.getByLabelText('Date de l’évènement'), tomorrow)
    await userEvent.type(screen.getByLabelText('Horaire 1'), '12:00')
    await userEvent.click(screen.getByText('Valider'))
    // stock line are here
    expect(await screen.findByText('Date')).toBeInTheDocument()

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )

    // stock line is not here anymore
    expect(screen.queryByText('Date')).not.toBeInTheDocument()
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
    expect(api.deleteStock).toHaveBeenCalledTimes(0)
  })

  it('should delete already created stocks', async () => {
    renderStockEventCreation({
      offer: individualOfferFactory({
        stocks: [individualStockFactory({ id: 12, priceCategoryId: 1 })],
      }),
    })

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[0]
    )
    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeInTheDocument()
  })
})
