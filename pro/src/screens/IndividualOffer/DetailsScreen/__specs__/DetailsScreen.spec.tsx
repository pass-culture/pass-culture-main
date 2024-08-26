import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { addressResponseIsEditableModelFactory } from 'utils/commonOffersApiFactories'
import {
  categoryFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { DetailsScreen, DetailsScreenProps } from '../DetailsScreen'
const mockLogEvent = vi.fn()

vi.mock('apiClient/api', () => ({
  api: {
    getMusicTypes: vi.fn(),
    postDraftOffer: vi.fn(),
    patchDraftOffer: vi.fn(),
    getSuggestedSubcategories: vi.fn(),
  },
}))

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

const scrollIntoViewMock = vi.fn()

const DEFAULTS = {
  mode: OFFER_WIZARD_MODE.CREATION,
  submitButtonLabel: 'Enregistrer et continuer',
}

const renderDetailsScreen = (
  props: DetailsScreenProps,
  contextValue: IndividualOfferContextValues,
  options: RenderWithProvidersOptions = {},
  mode: OFFER_WIZARD_MODE = DEFAULTS.mode
) => {
  const element = (
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsScreen {...props} />
    </IndividualOfferContext.Provider>
  )

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.DETAILS,
            mode,
          })}
          element={element}
        />
      </Routes>
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode,
        }),
      ],
      ...options,
    }
  )
}

describe('screens:IndividualOffer::Informations', () => {
  let props: DetailsScreenProps
  let contextValue: IndividualOfferContextValues
  let categories: CategoryResponseModel[]
  let subCategories: SubcategoryResponseModel[]

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    categories = [
      categoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
    ]
    subCategories = [
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: ['author', 'durationMinutes'],
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      subcategoryFactory({
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: ['ean', 'showType', 'gtl_id'],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      subcategoryFactory({
        id: 'physicalBis',
        categoryId: 'A',
        proLabel: 'Autre sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    props = {
      venues: [],
    }

    contextValue = individualOfferContextValuesFactory({
      categories,
      subCategories,
      offer: null,
    })
  })

  it('should render banner when no venue available', async () => {
    renderDetailsScreen(props, contextValue)

    expect(
      await screen.findByRole('heading', { name: 'À propos de votre offre' })
    ).toBeInTheDocument()
    expect(await screen.findByText(/Ajouter un lieu/)).toBeInTheDocument()
  })

  it('should render the component', async () => {
    renderDetailsScreen(
      {
        ...props,
        venues: [
          venueListItemFactory({ id: 189 }),
          venueListItemFactory({ id: 190 }),
        ],
      },
      contextValue
    )

    expect(
      await screen.findByRole('heading', { name: 'À propos de votre offre' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
    expect(screen.getByText(DEFAULTS.submitButtonLabel)).toBeInTheDocument()
  })

  it('should display the full form when categories, and subcategories has been selected', async () => {
    renderDetailsScreen(
      {
        ...props,
        venues: [
          venueListItemFactory({ id: 189 }),
          venueListItemFactory({ id: 190 }),
        ],
      },
      contextValue
    )
    await userEvent.selectOptions(
      await screen.findByLabelText('Catégorie *'),
      'A'
    )

    await userEvent.selectOptions(
      await screen.findByLabelText('Sous-catégorie *'),
      'physical'
    )
    expect(
      await screen.findByRole('heading', { name: 'Image de l’offre' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', { name: 'Informations artistiques' })
    ).toBeInTheDocument()
  })

  it('should not display the venues list when venues is <= 1', () => {
    props.venues = [venueListItemFactory({ id: 189 })]

    renderDetailsScreen(props, contextValue)

    expect(screen.queryByText(/Qui propose l’offre ?/)).not.toBeInTheDocument()
  })

  it('should show errors in the form when not all field has been filled', async () => {
    props.venues = [
      venueListItemFactory({ id: 189 }),
      venueListItemFactory({ id: 190 }),
    ]

    renderDetailsScreen(props, contextValue)

    await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))
    expect(
      screen.getByText('Veuillez sélectionner une catégorie')
    ).toBeInTheDocument()

    await userEvent.selectOptions(
      await screen.findByLabelText('Catégorie *'),
      'A'
    )
    await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))
    expect(
      screen.getByText('Veuillez sélectionner une sous-catégorie')
    ).toBeInTheDocument()

    await userEvent.selectOptions(
      await screen.findByLabelText('Sous-catégorie *'),
      'physical'
    )

    await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))
    expect(screen.getByText('Veuillez renseigner un titre')).toBeInTheDocument()
    expect(
      screen.getByText('Veuillez sélectionner un lieu')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Veuillez sélectionner un type de spectacle')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Veuillez sélectionner un sous-type de spectacle')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Veuillez sélectionner un genre musical')
    ).toBeInTheDocument()
  })

  it('should submit the form with correct payload', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'postDraftOffer').mockResolvedValue(
      getIndividualOfferFactory({
        id: 12,
      })
    )
    vi.spyOn(api, 'getMusicTypes').mockResolvedValue([
      { canBeEvent: true, label: 'Pop', gtl_id: 'pop' },
    ])
    props.venues = [
      venueListItemFactory({ id: 189 }),
      venueListItemFactory({ id: 190 }),
    ]

    renderDetailsScreen(props, contextValue)

    await userEvent.type(
      screen.getByLabelText(/Titre de l’offre/),
      'My super offer'
    )
    await userEvent.type(
      screen.getByLabelText(/Description/),
      'My super description'
    )

    await userEvent.selectOptions(await screen.findByLabelText(/Lieu/), '189')

    await userEvent.selectOptions(
      await screen.findByLabelText('Catégorie *'),
      'A'
    )

    await userEvent.selectOptions(
      await screen.findByLabelText('Sous-catégorie *'),
      'physical'
    )

    await userEvent.type(screen.getByLabelText(/EAN/), '1234567891234')
    await userEvent.selectOptions(
      await screen.findByLabelText(/Type de spectacle/),
      'Cirque'
    )
    await userEvent.selectOptions(
      await screen.findByLabelText(/Sous-type/),
      'Clown'
    )
    await userEvent.selectOptions(
      await screen.findByLabelText(/Genre musical/),
      'Pop'
    )

    await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))

    expect(api.postDraftOffer).toHaveBeenCalledOnce()
    expect(api.postDraftOffer).toHaveBeenCalledWith({
      description: 'My super description',
      extraData: {
        author: '',
        ean: '1234567891234',
        gtl_id: 'pop',
        showSubType: '205',
        showType: '200',
        performer: '',
        speaker: '',
        stageDirector: '',
        visa: '',
      },
      name: 'My super offer',
      subcategoryId: 'physical',
      venueId: 189,
    })
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        choosenSuggestedSubcategory: '',
        from: 'details',
        offerId: 12,
        offerType: 'individual',
        subcategoryId: 'physical',
        venueId: '189',
      }
    )
  })

  it('should submit the form with correct payload in edition', async () => {
    vi.spyOn(api, 'patchDraftOffer').mockResolvedValue(
      getIndividualOfferFactory({
        id: 12,
      })
    )
    vi.spyOn(api, 'getMusicTypes').mockResolvedValue([
      { canBeEvent: true, label: 'Pop', gtl_id: 'pop' },
    ])
    props.venues = [venueListItemFactory({ id: 189 })]
    contextValue.offer = getIndividualOfferFactory({
      id: 12,
      subcategoryId: 'physicalBis' as SubcategoryIdEnum,
    })

    renderDetailsScreen(props, contextValue)

    await userEvent.clear(screen.getByLabelText(/Titre de l’offre/))
    await userEvent.type(
      screen.getByLabelText(/Titre de l’offre/),
      'My super offer'
    )
    await userEvent.type(
      screen.getByLabelText(/Description/),
      'My super description'
    )

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(api.patchDraftOffer).toHaveBeenCalledOnce()
    expect(api.patchDraftOffer).toHaveBeenCalledWith(12, {
      description: 'My super description',
      durationMinutes: undefined,
      extraData: {
        author: 'Chuck Norris',
        ean: '1234567891234',
        gtl_id: '',
        performer: 'Le Poing de Chuck',
        showSubType: 'PEGI 18',
        showType: 'Cinéma',
        speaker: "Chuck Norris n'a pas besoin de doubleur",
        stageDirector: 'JCVD',
        visa: 'USA',
      },
      name: 'My super offer',
      subcategoryId: 'physicalBis',
    })
  })

  it('should render suggested subcategories', async () => {
    vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
      subcategoryIds: ['virtual', 'physical'],
    })

    renderDetailsScreen(
      {
        ...props,
        venues: [
          {
            id: 1,
            name: 'Venue 1',
            address: {
              ...addressResponseIsEditableModelFactory({
                label: 'mon adresse',
                city: 'ma ville',
                street: 'ma street',
                postalCode: '1',
              }),
            },
            isVirtual: false,
            hasCreatedOffer: false,
            managingOffererId: 1,
            offererName: 'Offerer 1',
            venueTypeCode: VenueTypeCode.FESTIVAL,
          },
          {
            id: 2,
            name: 'Venue 2',
            address: {
              ...addressResponseIsEditableModelFactory({
                label: 'mon adresse',
                city: 'ma ville',
                street: 'ma street',
                postalCode: '1',
              }),
            },
            isVirtual: false,
            hasCreatedOffer: false,
            managingOffererId: 1,
            offererName: 'Offerer 1',
            venueTypeCode: VenueTypeCode.FESTIVAL,
          },
        ],
      },
      contextValue,
      {
        features: ['WIP_SUGGESTED_SUBCATEGORIES'],
      }
    )

    // at first there is no suggested subcategories
    expect(
      screen.queryByText(/Catégories suggérées pour votre offre/)
    ).not.toBeInTheDocument()

    await userEvent.selectOptions(await screen.findByLabelText(/Lieu/), '1')

    await userEvent.type(
      screen.getByLabelText(/Titre de l’offre/),
      'My super offer'
    )

    // They appear after the first fields are filled
    expect(
      await screen.findByText(/Catégories suggérées pour votre offre/)
    ).toBeInTheDocument()
    expect(screen.getByText('Sous catégorie online de A')).toBeInTheDocument()
    expect(screen.getByText('Sous catégorie offline de A')).toBeInTheDocument()
    expect(screen.getByText('Autre')).toBeInTheDocument()

    // When clicking on a suggested subcategory, the conditional fields are displayed
    await userEvent.click(screen.getByText('Sous catégorie online de A'))
    expect(screen.getByText('Auteur')).toBeInTheDocument()
    expect(screen.getByText('Durée')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Sous catégorie offline de A'))
    expect(screen.queryByText('Auteur')).not.toBeInTheDocument()
    expect(screen.getByText(/EAN/)).toBeInTheDocument()

    // When clicking on "Autre", we can choose subcategory and the conditional fields are hidden
    await userEvent.click(screen.getByText('Autre'))
    expect(screen.queryByText('Auteur')).not.toBeInTheDocument()
    expect(screen.queryByText(/EAN/)).not.toBeInTheDocument()
    expect(screen.getByLabelText(/Catégorie/)).toBeInTheDocument()
  })

  it('should render error on category when no suggested categories has been selected', async () => {
    vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
      subcategoryIds: ['virtual', 'physical'],
    })

    renderDetailsScreen(
      {
        ...props,
        venues: [
          {
            id: 1,
            name: 'Venue 1',
            address: {
              ...addressResponseIsEditableModelFactory({
                label: 'mon adresse',
                city: 'ma ville',
                street: 'ma street',
                postalCode: '1',
              }),
            },
            isVirtual: false,
            hasCreatedOffer: false,
            managingOffererId: 1,
            offererName: 'Offerer 1',
            venueTypeCode: VenueTypeCode.FESTIVAL,
          },
          {
            id: 2,
            name: 'Venue 2',
            address: {
              ...addressResponseIsEditableModelFactory({
                label: 'mon adresse',
                city: 'ma ville',
                street: 'ma street',
                postalCode: '1',
              }),
            },
            isVirtual: false,
            hasCreatedOffer: false,
            managingOffererId: 1,
            offererName: 'Offerer 1',
            venueTypeCode: VenueTypeCode.FESTIVAL,
          },
        ],
      },
      contextValue,
      {
        features: ['WIP_SUGGESTED_SUBCATEGORIES'],
      }
    )

    // at first there is no suggested subcategories
    expect(
      screen.queryByText(/Catégories suggérées pour votre offre/)
    ).not.toBeInTheDocument()

    await userEvent.selectOptions(await screen.findByLabelText(/Lieu/), '1')

    await userEvent.type(
      screen.getByLabelText(/Titre de l’offre/),
      'My super offer'
    )

    expect(
      await screen.findByText(/Catégories suggérées pour votre offre/)
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))

    expect(
      screen.getByText('Veuillez sélectionner une catégorie')
    ).toBeInTheDocument()
  })

  describe('on creation', () => {
    it('should render EAN search for record stores as a venue', () => {
      const context = individualOfferContextValuesFactory({
        categories,
        subCategories,
        offer: null,
      })

      renderDetailsScreen(
        {
          ...props,
          venues: [
            venueListItemFactory({
              venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
            }),
          ],
        },
        context,
        { features: ['WIP_EAN_CREATION'] }
      )

      expect(
        screen.getByText(/Scanner ou rechercher un produit par EAN/)
      ).toBeInTheDocument()
    })

    it('should not render EAN search for other venues', () => {
      const context = individualOfferContextValuesFactory({
        categories,
        subCategories,
        offer: null,
      })

      renderDetailsScreen(
        {
          ...props,
          venues: [
            venueListItemFactory({
              venueTypeCode: VenueTypeCode.FESTIVAL,
            }),
          ],
        },
        context,
        { features: ['WIP_EAN_CREATION'] }
      )

      expect(
        screen.queryByText(/Scanner ou rechercher un produit par EAN/)
      ).not.toBeInTheDocument()
    })
  })

  describe('on edition', () => {
    it('should not render EAN search', () => {
      const context = individualOfferContextValuesFactory({
        categories,
        subCategories,
        offer: getIndividualOfferFactory({
          subcategoryId: 'physical' as SubcategoryIdEnum,
        }),
      })

      renderDetailsScreen(
        props,
        context,
        { features: ['WIP_EAN_CREATION'] },
        OFFER_WIZARD_MODE.EDITION
      )

      expect(
        screen.queryByText(/Scanner ou rechercher un produit par EAN/)
      ).not.toBeInTheDocument()
    })

    it('should not render suggested subcategories', () => {
      const context = individualOfferContextValuesFactory({
        categories,
        subCategories,
        offer: getIndividualOfferFactory({
          subcategoryId: 'physical' as SubcategoryIdEnum,
        }),
      })

      renderDetailsScreen(
        props,
        context,
        {
          features: ['WIP_SUGGESTED_SUBCATEGORIES'],
        },
        OFFER_WIZARD_MODE.EDITION
      )

      expect(
        screen.queryByText(/Catégories suggérées pour votre offre/)
      ).not.toBeInTheDocument()
      expect(screen.getByText('Type d’offre')).toBeInTheDocument()
      expect(
        screen.getByText('Sous catégorie offline de A')
      ).toBeInTheDocument()
    })
  })

  it('should not render venue field when there is just one venue', () => {
    props.venues = [venueListItemFactory({ id: 189 })]

    renderDetailsScreen(props, contextValue, {
      features: ['WIP_SUGGESTED_SUBCATEGORIES'],
    })

    expect(screen.queryByText(/Lieu/)).not.toBeInTheDocument()
  })
})
