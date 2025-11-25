import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
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
    { features: features }
  )
}

describe('IndividualOfferTimetable', () => {
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

    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({
        stocks: [],
        stockCount: 0,
      })
    )
  })

  it('should render the content of the offer timetable form', async () => {
    renderIndividualOfferTimetable(contextOverride)

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('heading', { name: 'Horaires' })
    ).toBeInTheDocument()
  })

  it('should not get the venue and openingHours if the FF WIP_ENABLE_OHO is disabled', async () => {
    const venuesSpy = vi.spyOn(api, 'getVenues')
    const oHsSpy = vi.spyOn(api, 'getOfferOpeningHours')

    renderIndividualOfferTimetable(contextOverride)

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(venuesSpy).not.toHaveBeenCalled()
    expect(oHsSpy).not.toHaveBeenCalled()
  })
})
