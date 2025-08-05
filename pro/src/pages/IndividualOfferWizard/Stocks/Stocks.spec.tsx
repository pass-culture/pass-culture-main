import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { screen, waitFor } from '@testing-library/react'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import * as useOfferWizardMode from 'commons/hooks/useOfferWizardMode'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { Stocks } from './Stocks'

vi.mock('apiClient/api', () => ({
  api: {
    getStocks: vi.fn(),
  },
}))

vi.mock('commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.EDITION),
}))

const renderStocksScreen = (
  contextOverride: Partial<IndividualOfferContextValues>,
  features: string[] = []
) => {
  const contextValue = individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <Stocks />
    </IndividualOfferContext.Provider>,
    { features: features }
  )
}

describe('screens:Stocks', () => {
  let contextOverride: IndividualOfferContextValues
  let offer: GetIndividualOfferWithAddressResponseModel
  const offerId = 12

  beforeEach(() => {
    offer = getIndividualOfferFactory({
      id: offerId,
      venue: getOfferVenueFactory({
        departementCode: '75',
      }),
    })
    contextOverride = individualOfferContextValuesFactory({
      offer,
    })

    vi.spyOn(api, 'getStocks').mockResolvedValue({
      stocks: [getOfferStockFactory()],
      hasStocks: true,
      stockCount: 1,
    })
  })

  it('should render stock thing', async () => {
    contextOverride.offer = getIndividualOfferFactory({
      ...contextOverride.offer,
      isEvent: false,
      isDigital: false,
    })
    renderStocksScreen(contextOverride)

    expect(
      await screen.findByText(
        'Les bénéficiaires ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()
  })

  it('should render stock event', async () => {
    contextOverride.offer = getIndividualOfferFactory({
      ...contextOverride.offer,
      isEvent: true,
    })
    renderStocksScreen(contextOverride)

    await waitFor(() => {
      expect(
        screen.getByText(
          'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible.'
        )
      ).toBeInTheDocument()
    })
  })

  const offerStatusWithoutBanner = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(offerStatusWithoutBanner)(
    'should not render stock description banner',
    async (offerStatus) => {
      contextOverride.offer = getIndividualOfferFactory({
        ...contextOverride.offer,
        isEvent: true,
        status: offerStatus,
      })
      renderStocksScreen(contextOverride)

      await waitFor(() => {
        expect(
          screen.queryByText(
            'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
          )
        ).not.toBeInTheDocument()
      })
    }
  )

  const offerStatusWithBanner = [
    OfferStatus.ACTIVE,
    OfferStatus.EXPIRED,
    OfferStatus.SOLD_OUT,
    OfferStatus.INACTIVE,
    OfferStatus.DRAFT,
  ]
  it.each(offerStatusWithBanner)(
    'should render stock description banner',
    async (offerStatus) => {
      contextOverride.offer = getIndividualOfferFactory({
        ...contextOverride.offer,
        isEvent: true,
        status: offerStatus,
      })
      renderStocksScreen(contextOverride)

      await waitFor(() => {
        expect(
          screen.queryByText(
            'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible.'
          )
        ).toBeInTheDocument()
      })
    }
  )

  it('should show the calendar form if the FF WIP_ENABLE_EVENT_WITH_OPENING_HOUR is enabled for an event creation', async () => {
    vi.spyOn(useOfferWizardMode, 'useOfferWizardMode').mockReturnValue(
      OFFER_WIZARD_MODE.CREATION
    )

    contextOverride.offer = getIndividualOfferFactory({
      ...contextOverride.offer,
      isEvent: true,
    })

    renderStocksScreen(contextOverride, ['WIP_ENABLE_EVENT_WITH_OPENING_HOUR'])

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('heading', { name: 'Dates et capacités' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })
})
