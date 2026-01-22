import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import type { IndividualOfferContextValues } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { getLocationResponseModel } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import type { RenderComponentFunction } from '@/commons/utils/renderWithProviders'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import {
  IndividualOfferSummaryDetailsScreen,
  type IndividualOfferSummaryDetailsScreenProps,
} from './IndividualOfferSummaryDetailsScreen'

const renderIndividualOfferSummaryDetailsScreen: RenderComponentFunction<
  IndividualOfferSummaryDetailsScreenProps,
  IndividualOfferContextValues
> = (params) => {
  const offer = params.props?.offer || getIndividualOfferFactory()

  const contextValues: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory({
      offer,
      categories: MOCKED_CATEGORIES,
      subCategories: MOCKED_SUBCATEGORIES,
    }),
    ...params.contextValues,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummaryDetailsScreen offer={offer} />
    </IndividualOfferContext.Provider>,
    params.options
  )
}

const LABELS = {
  buttons: {
    edit: 'Modifier',
    viewInApp: 'Visualiser dans l’app',
  },
  headings: {
    structure: 'Structure',
    accessibility: 'Modalités d’accessibilité',
  },
  texts: {
    ean: '1234567891234',
    publicVenueName: 'TATA',
    description: 'my description',
    productBasedCallout:
      "Ces informations proviennent de l'EAN et ne peuvent pas être modifiées.",
  },
}

describe('<IndividualOfferSummaryDetailsScreen />', () => {
  const offerBase = getIndividualOfferFactory({
    id: 1,
    name: 'Offre de test',
  })

  it('should render summary with filled data', () => {
    const offer = {
      ...offerBase,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE_WITH_EAN.id,
    }

    // Inject conditionalFields so EAN is displayed
    renderIndividualOfferSummaryDetailsScreen({ props: { offer } })

    expect(screen.getAllByText(offer.name)).toHaveLength(2)
    expect(
      screen.getByText(MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE_WITH_EAN.proLabel)
    ).toBeInTheDocument()
    expect(screen.getByText('1234567891234')).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: new RegExp(LABELS.buttons.edit) })
    ).toBeInTheDocument()
  })

  describe('when the offer is product based', () => {
    beforeEach(() => {
      const offer = {
        ...offerBase,
        subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
        productId: 1234567891234,
      }

      renderIndividualOfferSummaryDetailsScreen({ props: { offer } })
    })

    it('should display a callout telling that details cannot be edited', () => {
      expect(
        screen.getByText(new RegExp(LABELS.texts.productBasedCallout))
      ).toBeInTheDocument()
    })

    it('should not display an edit button', () => {
      const editButton = screen.queryByText(LABELS.buttons.edit)

      expect(editButton).not.toBeInTheDocument()
    })
  })

  it('should have "Structure" section', () => {
    const offer = {
      ...offerBase,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
      location: {
        ...getLocationResponseModel({
          label: 'mon adresse',
          city: 'ma ville',
          street: 'ma street',
          postalCode: '1',
        }),
      },
      venue: getOfferVenueFactory(),
    }

    renderIndividualOfferSummaryDetailsScreen({ props: { offer } })

    expect(
      screen.getByText(new RegExp(LABELS.headings.structure))
    ).toBeInTheDocument()
    expect(screen.getByText(/Nom public de la structure/)).toBeInTheDocument()
  })

  it('should have "Structure" section with publicName', () => {
    const offer = {
      ...offerBase,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
      location: {
        ...getLocationResponseModel({
          label: 'mon adresse',
          city: 'ma ville',
          street: 'ma street',
          postalCode: '1',
        }),
      },
      venue: getOfferVenueFactory({ publicName: LABELS.texts.publicVenueName }),
    }

    renderIndividualOfferSummaryDetailsScreen({ props: { offer } })

    expect(
      screen.getByText(new RegExp(LABELS.headings.structure))
    ).toBeInTheDocument()
    expect(screen.getByText(LABELS.texts.publicVenueName)).toBeInTheDocument()
  })

  it('should show the description of the offer', () => {
    const offer = {
      ...offerBase,
      description: LABELS.texts.description,
    }

    renderIndividualOfferSummaryDetailsScreen({ props: { offer } })

    //  The description is displayed twice : once in the summary and once in the preview
    expect(screen.getAllByText(LABELS.texts.description)).toHaveLength(2)
    expect(screen.getAllByTestId('markdown-content')).toHaveLength(2)
  })

  it('should not show the description if the offer has no description', () => {
    const offer = {
      ...offerBase,
      description: '',
    }

    renderIndividualOfferSummaryDetailsScreen({ props: { offer } })

    expect(screen.queryByTestId('markdown-content')).not.toBeInTheDocument()
  })

  it('should have "Modalités d’accessibilité" section', () => {
    const offer = {
      ...offerBase,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: false,
    }

    renderIndividualOfferSummaryDetailsScreen({ props: { offer } })

    expect(screen.getByText(LABELS.headings.accessibility)).toBeInTheDocument()
    expect(screen.getByText('Auditif')).toBeInTheDocument()
    expect(screen.queryByText('Psychique ou cognitif')).not.toBeInTheDocument()
    expect(screen.getByText('Moteur')).toBeInTheDocument()
    expect(screen.queryByText('Visuel')).not.toBeInTheDocument()
  })

  it('should NOT display the offer URL when offer is digital', () => {
    const offer = {
      ...offerBase,
      isDigital: true,
      url: 'https://example.com/mon-offre',
    }

    renderIndividualOfferSummaryDetailsScreen({
      props: { offer },
    })

    expect(screen.queryByText(/URL d’accès à l’offre/i)).not.toBeInTheDocument()
    expect(screen.queryByText(offer.url)).not.toBeInTheDocument()
  })
})
