import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  getStocksResponseFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferTimetable } from './IndividualOfferTimetable'

vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
}))

const renderIndividualOfferTimetable = (
  contextOverride: Partial<IndividualOfferContextValues>,
  features: string[] = []
) => {
  const contextValue = individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferTimetable />
    </IndividualOfferContext.Provider>,
    {
      features: features,
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    }
  )
}

describe('IndividualOfferTimetable', () => {
  let contextOverride: IndividualOfferContextValues
  let offer: GetIndividualOfferResponseModelV2
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

    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
      })
    )
  })

  it('should render the content of the offer timetable form', async () => {
    renderIndividualOfferTimetable(contextOverride)

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('heading', { name: 'Horaires et stocks' })
    ).toBeInTheDocument()
  })
})
