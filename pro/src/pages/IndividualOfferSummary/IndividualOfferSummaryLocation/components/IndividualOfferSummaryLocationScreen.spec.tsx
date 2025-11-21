import { screen, within } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  IndividualOfferSummaryLocationScreen,
  type IndividualOfferSummaryLocationScreenProps,
} from './IndividualOfferSummaryLocationScreen'

const useOfferWizardModeMock = vi.hoisted(() =>
  vi.fn(() => OFFER_WIZARD_MODE.READ_ONLY)
)
vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: useOfferWizardModeMock,
}))

const renderIndividualOfferSummaryLocationScreen: RenderComponentFunction<
  IndividualOfferSummaryLocationScreenProps
> = (params) => {
  const props: IndividualOfferSummaryLocationScreenProps = {
    offer: getIndividualOfferFactory(),
    ...params.props,
  }

  return renderWithProviders(
    <IndividualOfferSummaryLocationScreen {...props} />,
    params.options
  )
}

const LABELS = {
  buttons: {
    edit: 'Modifier la localisation de l’offre',
    viewInApp: 'Visualiser dans l’app',
  },
  fields: {
    addressLabel: /Intitulé/,
    address: /Adresse/,
    url: /URL d’accès à l’offre/,
  },
  headings: {
    main: 'Localisation',
    sub: 'Où profiter de l’offre ?',
    appPreview: 'Aperçu dans l’app',
  },
} as const

describe('<IndividualOfferSummaryLocationScreen />', () => {
  describe('for a physical offer', () => {
    const physicalOffer = getIndividualOfferFactory({
      isDigital: false,
      location: {
        id: 1,
        label: "Le lieu de l'offre",
        street: '1 rue de la paix',
        postalCode: '75001',
        city: 'Paris',
        latitude: 48.8,
        longitude: 2.3,
        isManualEdition: false,
        isVenueLocation: true,
        banId: '75101_xxxx',
        inseeCode: '75101',
      },
    })

    it('should render and pass accessibility checks', async () => {
      const { container } = renderIndividualOfferSummaryLocationScreen({
        props: { offer: physicalOffer },
      })

      expect(
        await screen.findByRole('heading', { name: LABELS.headings.main })
      ).toBeInTheDocument()
      expect(await axe(container)).toHaveNoViolations()
    })

    it('should display location information', () => {
      const { container } = renderIndividualOfferSummaryLocationScreen({
        props: { offer: physicalOffer },
      })

      const mainContent = container.querySelector(
        '.summary-layout-content'
      ) as HTMLElement
      expect(mainContent).toBeInTheDocument()

      expect(
        within(mainContent).getByRole('heading', { name: LABELS.headings.main })
      ).toBeInTheDocument()
      expect(
        within(mainContent).getByRole('link', { name: LABELS.buttons.edit })
      ).toBeInTheDocument()
      expect(
        within(mainContent).getByRole('heading', { name: LABELS.headings.sub })
      ).toBeInTheDocument()
      expect(
        within(mainContent).getByText(LABELS.fields.addressLabel)
      ).toBeInTheDocument()
      expect(
        within(mainContent).getByText("Le lieu de l'offre")
      ).toBeInTheDocument()
      expect(
        within(mainContent).getByText(LABELS.fields.address)
      ).toBeInTheDocument()
      expect(
        within(mainContent).getByText('1 rue de la paix 75001 Paris')
      ).toBeInTheDocument()
    })

    it('should not display URL information', () => {
      renderIndividualOfferSummaryLocationScreen({
        props: { offer: physicalOffer },
      })
      expect(screen.queryByText(LABELS.fields.url)).not.toBeInTheDocument()
    })
  })

  describe('for a digital offer', () => {
    const digitalOffer = getIndividualOfferFactory({
      isDigital: true,
      url: 'https://pass.culture.fr',
    })

    it('should render and pass accessibility checks', async () => {
      const { container } = renderIndividualOfferSummaryLocationScreen({
        props: { offer: digitalOffer },
      })

      expect(
        await screen.findByRole('heading', { name: LABELS.headings.main })
      ).toBeInTheDocument()
      expect(await axe(container)).toHaveNoViolations()
    })

    it('should display URL information', () => {
      renderIndividualOfferSummaryLocationScreen({
        props: { offer: digitalOffer },
      })

      expect(
        screen.getByRole('heading', { name: LABELS.headings.main })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: LABELS.buttons.edit })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: LABELS.headings.sub })
      ).toBeInTheDocument()
      expect(screen.getByText(LABELS.fields.url)).toBeInTheDocument()
      expect(screen.getByText('https://pass.culture.fr')).toBeInTheDocument()
    })

    it('should not display physical location information', () => {
      renderIndividualOfferSummaryLocationScreen({
        props: { offer: digitalOffer },
      })
      expect(
        screen.queryByText(LABELS.fields.addressLabel)
      ).not.toBeInTheDocument()
      expect(screen.queryByText(LABELS.fields.address)).not.toBeInTheDocument()
    })
  })
})
