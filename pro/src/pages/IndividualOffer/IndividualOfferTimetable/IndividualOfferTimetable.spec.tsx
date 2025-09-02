import { screen, waitFor } from '@testing-library/react'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferTimetable } from './IndividualOfferTimetable'

vi.mock('@/apiClient/api', () => ({
  api: {
    getStocks: vi.fn(() => ({ stocks: [] })),
    getOpeningHours: vi.fn(),
  },
}))

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
  })

  it('should render the content of the offer timetable form', async () => {
    renderIndividualOfferTimetable(contextOverride)

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('heading', { name: 'Dates et capacités' })
    ).toBeInTheDocument()
  })
})
