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

vi.mock('apiClient/api', () => ({
  api: {
    getMusicTypes: vi.fn(),
    postDraftOffer: vi.fn(),
    patchDraftOffer: vi.fn(),
    getSuggestedSubcategories: vi.fn(),
    getProductByEan: vi.fn(),
  },
}))

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

vi.mock('use-debounce', async () => ({
  ...(await vi.importActual('use-debounce')),
  useDebouncedCallback: vi.fn((fn) => fn),
}))

const mockLogEvent = vi.fn()
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
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedOffererId: 1,
        },
      },
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
      subcategoryFactory({
        id: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
        categoryId: 'MUSIQUE_ENREGISTREE',
        proLabel: 'Vinyles et autres supports',
        conditionalFields: ['gtl_id', 'author', 'performer', 'ean'],
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

  it('should display error from api on fields', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'postDraftOffer').mockRejectedValue({
      message: 'oups',
      name: 'ApiError',
      body: { ean: 'broken ean from api' },
    })
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

    expect(screen.getByText('broken ean from api')).toBeInTheDocument()
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

  describe('about categories / subcategories selection', () => {
    const venueSelectorLabel = /Lieu/
    const titleLabel = /Titre de l’offre/
    const suggestedSubCatTitle = /Catégories suggérées pour votre offre/
    const suggestedSubCatEmptyState =
      /Veuillez renseigner un titre ou une description/
    const customProps = {
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
    }

    it('should render suggested subcategories when enabled', async () => {
      const chosenSubCategoriesIds = ['virtual', 'physical']
      vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
        subcategoryIds: chosenSubCategoriesIds,
      })
      vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
        SUGGESTED_CATEGORIES: 'true',
      })

      renderDetailsScreen(customProps, contextValue, {
        features: ['WIP_SUGGESTED_SUBCATEGORIES'],
      })

      // User selects a venue or fills the title.
      const venueSelector = screen.getByLabelText(venueSelectorLabel)
      const titleInput = screen.getByLabelText(titleLabel)
      await userEvent.selectOptions(venueSelector, '1')
      await userEvent.type(titleInput, 'My super offer')

      // Suggested subcategories are displayed along with the "Autre" option.
      const radioButtons = screen.getAllByRole('radio')
      expect(radioButtons).toHaveLength(chosenSubCategoriesIds.length + 1)
    })

    it('should fallback to manual selection when suggested subcategories are enabled but not available', async () => {
      // An empty array of suggestions will be handled the same way as an api error.
      // To test this, we either mock the api call to return an empty array or reject the promise.
      vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
        subcategoryIds: [],
      })
      vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
        SUGGESTED_CATEGORIES: 'true',
      })

      renderDetailsScreen(customProps, contextValue, {
        features: ['WIP_SUGGESTED_SUBCATEGORIES'],
      })

      // User selects a venue or fills the title.
      const venueSelector = screen.getByLabelText(venueSelectorLabel)
      const titleInput = screen.getByLabelText(titleLabel)
      await userEvent.selectOptions(venueSelector, '1')
      await userEvent.type(titleInput, 'My super offer')

      // Only the "Autre" option should be available and selected.
      const radioButtons = screen.getAllByRole('radio')
      expect(radioButtons).toHaveLength(1)
    })

    it('should render an error when no selection has been made', async () => {
      vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
        subcategoryIds: ['virtual', 'physical'],
      })
      vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
        SUGGESTED_CATEGORIES: 'true',
      })

      renderDetailsScreen(customProps, contextValue, {
        features: ['WIP_SUGGESTED_SUBCATEGORIES'],
      })

      // Init.
      const title = screen.getByText(suggestedSubCatTitle)
      expect(title).toBeInTheDocument()
      const initText = screen.queryByText(suggestedSubCatEmptyState)
      expect(initText).toBeInTheDocument()

      // User selects a venue or fills the title.
      const venueSelector = screen.getByLabelText(venueSelectorLabel)
      const titleInput = screen.getByLabelText(titleLabel)
      await userEvent.selectOptions(venueSelector, '1')
      await userEvent.type(titleInput, 'My super offer')

      // User doesn't select anything and submits.
      expect(initText).not.toBeInTheDocument()
      await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))
      const error = screen.getByText('Veuillez sélectionner une catégorie')
      expect(error).toBeInTheDocument()
    })
  })

  it('should display first venue banner when venues are empty and suggested categories not enable', () => {
    renderDetailsScreen(
      {
        ...props,
        venues: [],
      },
      contextValue
    )
    expect(
      screen.getByText(
        'Pour créer une offre dans cette catégorie, ajoutez d’abord un lieu à votre structure.'
      )
    ).toBeInTheDocument()
  })

  it('should display second venue banner when only one virtual venue and not virtual subcategory chosen', async () => {
    vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
      subcategoryIds: ['virtual', 'physical'],
    })
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      SUGGESTED_CATEGORIES: 'true',
    })

    renderDetailsScreen(
      {
        ...props,
        venues: [venueListItemFactory({ id: 189, isVirtual: true })],
      },
      contextValue,
      { features: ['WIP_SUGGESTED_SUBCATEGORIES'] }
    )
    await userEvent.type(screen.getByLabelText(/Titre de l’offre/), 'My title')
    await userEvent.click(
      await screen.findByText('Sous catégorie offline de A')
    )

    expect(
      screen.getByText(
        'Pour créer une offre dans cette catégorie, ajoutez d’abord un lieu à votre structure.'
      )
    ).toBeInTheDocument()
    expect(screen.queryByText('Image de l’offre')).not.toBeInTheDocument()
  })

  describe('on creation', () => {
    describe('about EAN search', () => {
      const eanSearchTitle = /Scanner ou rechercher un produit par EAN/
      const eanInputLabel = /Nouveau Scanner ou rechercher un produit par EAN/
      const eanButtonLabel = /Rechercher/

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

        expect(screen.getByText(eanSearchTitle)).toBeInTheDocument()
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

        expect(screen.queryByText(eanSearchTitle)).not.toBeInTheDocument()
      })

      it('should prefill the form with EAN search result', async () => {
        const ean = '9781234567897'
        const productData = {
          id: 0,
          name: 'Music has the right to children',
          description: 'An album by Boards of Canada',
          subcategoryId: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
          gtlId: '08000000',
          author: 'Boards of Canada',
          performer: 'Boards of Canada',
          images: {
            recto: 'https://www.example.com/image.jpg',
          },
        }

        const context = individualOfferContextValuesFactory({
          categories,
          subCategories,
          offer: null,
        })

        vi.spyOn(api, 'getProductByEan').mockResolvedValue(productData)
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

        const button = screen.getByRole('button', { name: eanButtonLabel })
        const input = screen.getByRole('textbox', { name: eanInputLabel })

        await userEvent.type(input, ean)
        await userEvent.click(button)

        // Inputs are filled with the product data and image is displayed.
        const nameInputLabel = /Titre de l’offre/
        const inputName = screen.getByRole('textbox', { name: nameInputLabel })
        const image = screen.getByTestId('image-preview')
        expect(inputName).toHaveValue(productData.name)
        expect(image).toHaveAttribute('src', productData.images.recto)

        // Inputs are disabled and image cannot be changed.
        expect(inputName).toBeDisabled()
        const imageEditLabel = /Ajouter une image/
        const imageEditButton = screen.queryByRole('button', {
          name: imageEditLabel,
        })
        expect(imageEditButton).not.toBeInTheDocument()
      })
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
      vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
        SUGGESTED_CATEGORIES: 'true',
      })
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
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      SUGGESTED_CATEGORIES: 'true',
    })
    props.venues = [venueListItemFactory({ id: 189 })]

    renderDetailsScreen(props, contextValue, {
      // There is no world where WIP_SUGGESTED_SUBCATEGORIES is enabled without WIP_SPLIT_OFFER
      features: ['WIP_SPLIT_OFFER', 'WIP_SUGGESTED_SUBCATEGORIES'],
    })

    expect(screen.queryByText(/Lieu/)).not.toBeInTheDocument()
  })
})
