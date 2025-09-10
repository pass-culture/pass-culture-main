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

import { IndividualOfferSummaryLocation } from './IndividualOfferSummaryLocation'

// Keep ActionBar mocked only to assert SUMMARY step like original test.
vi.mock('@/pages/IndividualOffer/components/ActionBar/ActionBar', () => ({
  ActionBar: ({ step }: { step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS }) => (
    <div data-testid="action-bar">step:{step}</div>
  ),
}))

const renderIndividualOfferSummaryLocation: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params = {}) => {
  const offer = getIndividualOfferFactory({ id: 1 })
  const path = getIndividualOfferPath({
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.CREATION,
  })

  const contextValues = individualOfferContextValuesFactory({
    offer,
    ...params.contextValues,
  })
  const options = {
    initialRouterEntries: [path],
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummaryLocation />
    </IndividualOfferContext.Provider>,
    options
  )
}

const LABELS = {
  headings: {
    location: 'Localisation',
  },
  texts: {
    spinner: 'Chargement en cours',
  },
}

describe('<IndividualOfferSummaryLocation />', () => {
  it('should show a spinner while offer is null', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: null,
    })

    renderIndividualOfferSummaryLocation({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
    expect(screen.getByText(LABELS.texts.spinner)).toBeInTheDocument()
  })

  it('should render the layout with title and nested screen when offer is present', () => {
    renderIndividualOfferSummaryLocation({})

    expect(
      screen.getByRole('heading', { name: LABELS.headings.location })
    ).toBeInTheDocument()
  })

  it('should render the ActionBar for the SUMMARY step', () => {
    renderIndividualOfferSummaryLocation({})

    const actionBar = screen.getByTestId('action-bar')
    expect(actionBar).toHaveTextContent(
      `step:${INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}`
    )
  })
})
