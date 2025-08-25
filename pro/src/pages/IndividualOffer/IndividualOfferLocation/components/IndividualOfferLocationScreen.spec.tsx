import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '../../commons/__mocks__/constants'
import {
  IndividualOfferLocationScreen,
  type IndividualOfferLocationScreenProps,
} from './IndividualOfferLocationScreen'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
  },
}))

const renderIndividualOfferLocationScreen: RenderComponentFunction<
  IndividualOfferLocationScreenProps,
  IndividualOfferContextValues
> = (params) => {
  const offer = getIndividualOfferFactory()
  const venues = [
    {
      ...makeVenueListItem({
        id: 1,
        publicName: 'Lieu Nom Public Pour Test',
      }),
      address: {
        banId: '75101_9575_00003',
        city: 'Paris',
        id: 945,
        id_oa: 1,
        inseeCode: '75056',
        isLinkedToVenue: false,
        isManualEdition: false,
        label: 'MINISTERE DE LA CULTURE',
        latitude: 48.87171,
        longitude: 2.30829,
        postalCode: '75001',
        street: '3 Rue de Valois',
      },
    },
  ]
  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    isAccessibilityFilled: false,
    isEvent: null,
    setIsAccessibilityFilled: vi.fn(),
    setIsEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    offer,
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }
  const props: IndividualOfferLocationScreenProps = {
    offer,
    venues,
    ...params.props,
  }

  // Ensure components reading offer from context (e.g., LocationForm) get the same offer as props by default
  contextValues.offer = props.offer ?? contextValues.offer

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferLocationScreen {...props} />
    </IndividualOfferContext.Provider>,
    options
  )
}

const LABELS = {
  titles: {
    main: 'Où profiter de l’offre ?',
  },
  buttons: {
    save: 'Enregistrer et continuer',
    cantFindAddress: /Vous ne trouvez pas votre adresse \?/,
  },
  fields: {
    address: `Il s’agit de l’adresse à laquelle les jeunes devront se présenter.`,
    url: `URL d’accès à l’offre *`,
    addressLocationLabel: 'Intitulé de la localisation',
    street: 'Adresse postale',
    postalCode: 'Code postal',
    city: 'Ville',
    coords: 'Coordonnées GPS',
  },
  options: {
    venueAddress: 'Lieu Nom Public Pour Test – 3 Rue de Valois 75001 Paris',
    otherAddress: 'À une autre adresse',
  },
}

describe('<IndividualOfferLocationScreen />', () => {
  const offlineOffer = getIndividualOfferFactory({
    id: 3,
    subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
    venue: getOfferVenueFactory({ id: 1 }),
  })
  const onlineOffer = {
    ...offlineOffer,
    subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_ONLINE.id,
  }

  it('should render the screen', async () => {
    const props = { offer: offlineOffer }

    renderIndividualOfferLocationScreen({ props })

    expect(
      await screen.findByRole('heading', { name: LABELS.titles.main })
    ).toBeInTheDocument()
  })

  it('should submit the venue address payload when a venue address is selected', async () => {
    vi.spyOn(api, 'patchOffer').mockResolvedValue(offlineOffer)

    const props = { offer: offlineOffer }

    renderIndividualOfferLocationScreen({ props })

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Lieu Nom Public Pour Test – 3 Rue de Valois 75001 Paris',
      })
    )

    await userEvent.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(api.patchOffer).toHaveBeenCalledOnce()
    expect(api.patchOffer).toHaveBeenCalledWith(
      3,
      expect.objectContaining({
        address: expect.objectContaining({
          city: 'Paris',
          isManualEdition: false,
          isVenueAddress: true,
          locationLabel: 'MINISTERE DE LA CULTURE',
          latitude: '48.87171',
          longitude: '2.30829',
          postalCode: '75001',
          street: '3 Rue de Valois',
          banId: '75101_9575_00003',
          inseeCode: '75056',
        }),
        shouldSendMail: false,
        url: null,
      })
    )
  })

  it('should disable the physical location inputs if another offer with the same EAN exists', async () => {
    const contextValues = { hasPublishedOfferWithSameEan: true }
    const props = { offer: offlineOffer }

    renderIndividualOfferLocationScreen({ contextValues, props })

    expect(
      await screen.findByRole('radiogroup', {
        name: LABELS.fields.address,
      })
    ).toHaveAttribute('aria-disabled', 'true')
  })

  describe('online subcategory', () => {
    beforeEach(() => {
      vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
        useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.EDITION),
      }))
    })
    it('should show only the URL field', async () => {
      const props = { offer: onlineOffer }

      renderIndividualOfferLocationScreen({ props })

      expect(
        await screen.findByRole('heading', { name: LABELS.titles.main })
      ).toBeInTheDocument()

      expect(
        screen.getByRole('textbox', { name: LABELS.fields.url })
      ).toBeInTheDocument()

      expect(
        screen.queryByRole('radiogroup', {
          name: LABELS.fields.address,
        })
      ).not.toBeInTheDocument()
    })

    it('should disable the URL field if another offer with the same EAN exists', async () => {
      const contextValues = { hasPublishedOfferWithSameEan: true }
      const props = { offer: onlineOffer }

      renderIndividualOfferLocationScreen({ contextValues, props })

      expect(
        await screen.findByRole('textbox', { name: LABELS.fields.url })
      ).toBeDisabled()
    })

    it('should render without error in CREATION mode even if URL is initially null', async () => {
      vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
        useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
      }))
      const props = { offer: { ...onlineOffer, url: null } }

      renderIndividualOfferLocationScreen({ props })

      expect(
        await screen.findByRole('heading', { name: LABELS.titles.main })
      ).toBeInTheDocument()

      expect(
        screen.getByRole('textbox', { name: LABELS.fields.url })
      ).toBeInTheDocument()
    })
  })

  describe('read-only mode', () => {
    beforeEach(() => {
      vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
        useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.READ_ONLY),
      }))
    })

    it('should disable all fields for offline offer', async () => {
      const props = { offer: offlineOffer }
      const contextValues = { hasPublishedOfferWithSameEan: false }

      renderIndividualOfferLocationScreen({ props, contextValues })

      expect(
        await screen.findByRole('radiogroup', {
          name: LABELS.fields.address,
        })
      ).toHaveAttribute('aria-disabled', 'true')
    })

    it('should disable the URL field for online offer', async () => {
      const props = { offer: onlineOffer }
      const contextValues = { hasPublishedOfferWithSameEan: false }

      renderIndividualOfferLocationScreen({ props, contextValues })

      expect(
        await screen.findByRole('textbox', { name: LABELS.fields.url })
      ).toBeDisabled()
    })
  })
})
