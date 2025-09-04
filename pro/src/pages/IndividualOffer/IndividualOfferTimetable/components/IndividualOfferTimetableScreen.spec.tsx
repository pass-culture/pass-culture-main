import { screen, waitFor } from '@testing-library/react'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualOfferTimetableScreen,
  type IndividualOfferTimetableScreenProps,
} from './IndividualOfferTimetableScreen'

const defaultProps: IndividualOfferTimetableScreenProps = {
  mode: OFFER_WIZARD_MODE.CREATION,
  offer: getIndividualOfferFactory(),
  stocks: [],
  openingHours: null,
}

function renderIndividualOfferTimetableScreen(
  props?: Partial<IndividualOfferTimetableScreenProps>,
  features?: string[]
) {
  return renderWithProviders(
    <IndividualOfferTimetableScreen {...defaultProps} {...props} />,
    { features: features }
  )
}

describe('IndividualOfferTimetableScreen', () => {
  it('should render the timetable type choice', async () => {
    renderIndividualOfferTimetableScreen(
      { offer: getIndividualOfferFactory({ isEvent: true, hasStocks: false }) },
      ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW', 'WIP_ENABLE_OHO']
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('radiogroup', { name: /Quand profiter de l’offre/ })
    ).toBeInTheDocument()
  })

  it('should not render the timetable type choice if the WIP_ENABLE_OHO FF is disabled', async () => {
    renderIndividualOfferTimetableScreen(
      { offer: getIndividualOfferFactory({ isEvent: true, hasStocks: false }) },
      ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW']
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByRole('radiogroup', { name: /Quand profiter de l’offre/ })
    ).not.toBeInTheDocument()
  })

  it('should not render the timetable type choice if the WIP_ENABLE_NEW_OFFER_CREATION_FLOW FF is disabled', async () => {
    renderIndividualOfferTimetableScreen(
      { offer: getIndividualOfferFactory({ isEvent: true, hasStocks: false }) },
      ['WIP_ENABLE_OHO']
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByRole('radiogroup', { name: /Quand profiter de l’offre/ })
    ).not.toBeInTheDocument()
  })
})
