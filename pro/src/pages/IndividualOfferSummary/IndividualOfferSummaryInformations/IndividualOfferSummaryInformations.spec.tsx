import { screen } from '@testing-library/react'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummaryInformations } from './IndividualOfferSummaryInformations'

const LABELS = {
  headings: {
    layout: 'Récapitulatif',
    informations: 'Informations pratiques',
    location: 'Localisation',
  },
  buttons: {
    publish: 'Publier l’offre',
  },
  texts: {
    spinner: 'Chargement en cours',
  },
}

const renderIndividualOfferSummaryInformations: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params = {}) => {
  const offer = getIndividualOfferFactory({ id: 1 })
  const path = getIndividualOfferPath({
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.CREATION,
  })

  const contextValues = individualOfferContextValuesFactory({
    offer: offer,
    ...params.contextValues,
  })
  const options = {
    initialRouterEntries: [path],
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummaryInformations />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferSummaryInformations />', () => {
  it('should show a spinner while offer is null', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: null,
    })

    renderIndividualOfferSummaryInformations({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
    expect(screen.getByText(LABELS.texts.spinner)).toBeInTheDocument()
  })

  it('should render location summary when feature flag is active', () => {
    renderIndividualOfferSummaryInformations({
      options: { features: ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'] },
    })

    expect(
      screen.getByRole('heading', { name: LABELS.headings.location })
    ).toBeInTheDocument()
  })

  it('should render informations layout and nested screen when feature flag is inactive', () => {
    renderIndividualOfferSummaryInformations({})

    expect(
      screen.getByRole('heading', { name: LABELS.headings.layout })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: LABELS.headings.informations })
    ).toBeInTheDocument()
  })

  it('should render ActionBar publish button in creation mode summary step', () => {
    renderIndividualOfferSummaryInformations({})

    expect(
      screen.getByRole('button', { name: LABELS.buttons.publish })
    ).toBeInTheDocument()
  })
})
