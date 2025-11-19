import { screen } from '@testing-library/react'

import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummaryInformations } from './IndividualOfferSummaryInformations'

const LABELS = {
  headings: {
    informations: 'Informations pratiques',
    location: 'Localisation',
  },
  buttons: {
    publish: 'Publier l’offre',
  },
}

const renderIndividualOfferSummaryInformations = () => {
  const offer = getIndividualOfferFactory({ id: 1 })
  const path = getIndividualOfferPath({
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.CREATION,
  })

  const contextValues = individualOfferContextValuesFactory({
    offer: offer,
  })
  const options = {
    initialRouterEntries: [path],
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummaryInformations />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferSummaryInformations />', () => {
  it('should render location summary when feature flag is active', () => {
    renderIndividualOfferSummaryInformations()

    expect(
      screen.getByRole('heading', { name: LABELS.headings.location })
    ).toBeInTheDocument()
  })

  it('should render ActionBar publish button in creation mode summary step', () => {
    renderIndividualOfferSummaryInformations()

    expect(
      screen.getByRole('button', { name: LABELS.buttons.publish })
    ).toBeInTheDocument()
  })
})
