import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'
import { beforeEach } from 'vitest'

import { api } from 'apiClient/api'
import {
  OfferStatus,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  CATEGORY_STATUS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import {
  categoryFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'

import {
  IndividualOfferDetailsScreen,
  IndividualOfferDetailsScreenProps,
} from './IndividualOfferDetailsScreen'

vi.mock('apiClient/api', () => ({
  api: {
    getMusicTypes: vi.fn(),
    postDraftOffer: vi.fn(),
    patchDraftOffer: vi.fn(),
    getProductByEan: vi.fn(),
    getActiveVenueOfferByEan: vi.fn(),
  },
}))

vi.mock('commons/utils/windowMatchMedia', () => ({
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

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: vi.fn(),
}))
const mockNavigate = vi.fn()

const MOCK_DATA = {
  title: 'My super offer',
  description: 'My super description',
  venues: [
    venueListItemFactory({ id: 189 }),
    venueListItemFactory({ id: 190 }),
  ],
  categories: [
    categoryFactory({
      id: 'A',
      proLabel: 'Catégorie A',
      isSelectable: true,
    }),
  ],
  subCategories: [
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
      canBeWithdrawable: false,
      onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
    }),
    subcategoryFactory({
      id: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
      categoryId: 'MUSIQUE_ENREGISTREE',
      proLabel: 'Vinyles et autres supports',
      conditionalFields: ['gtl_id', 'author', 'performer', 'ean'],
    }),
  ],
  ean: '1234567891234',
  showType: 'Cirque',
  showSubType: 'Clown',
  musicType: 'Pop',
}

const LABELS = {
  title: /Titre de l’offre/,
  description: /Description/,
  venue: /Qui propose l’offre ?/,
  category: /Catégorie/,
  subcategory: /Sous-catégorie/,
  ean: /EAN/,
  showType: /Type de spectacle/,
  showSubType: /Sous-type/,
  musicType: /Genre musical/,
}

const renderDetailsScreen = ({
  props,
  contextValue,
  options = {},
  mode = DEFAULTS.mode,
  initialRoute = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.DETAILS,
    mode,
  }),
}: {
  props?: IndividualOfferDetailsScreenProps
  contextValue: IndividualOfferContextValues
  options?: RenderWithProvidersOptions
  mode?: OFFER_WIZARD_MODE
  initialRoute?: string
}) => {
  const finalProps = {
    ...(props || {}),
    venues: props?.venues || MOCK_DATA.venues,
  }

  const element = (
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferDetailsScreen {...finalProps} />
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
        <Route
          path={`/onboarding${getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.DETAILS,
            mode,
          })}`}
          element={element}
        />
      </Routes>
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialRoute],
      ...options,
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
    }
  )
}

// User always selects 'physical' subcategory and fills related fields
// (e.g: EAN, showType, showSubType, musicType conditional fields).
// Mind that vi.spyOn(api, 'getMusicTypes').mockResolvedValue([
// { canBeEvent: true, label: 'Pop', gtl_id: 'pop' },
// ]) must be added to the test file where this function is called.
const userFillsEverything = async () => {
  await userEvent.type(screen.getByLabelText(LABELS.title), MOCK_DATA.title)
  await userEvent.type(
    screen.getByLabelText(LABELS.description),
    MOCK_DATA.description
  )
  await userEvent.selectOptions(
    await screen.findByLabelText(LABELS.venue),
    MOCK_DATA.venues[0].id.toString()
  )

  await userEvent.selectOptions(
    await screen.findByLabelText(LABELS.category),
    MOCK_DATA.categories[0].id
  )
  await userEvent.selectOptions(
    await screen.findByLabelText(LABELS.subcategory),
    (
      MOCK_DATA.subCategories.find(
        (s) => s.id === 'physical'
      ) as SubcategoryResponseModel
    ).proLabel
  )

  await userEvent.type(screen.getByLabelText(LABELS.ean), MOCK_DATA.ean)
  await userEvent.selectOptions(
    await screen.findByLabelText(LABELS.showType),
    MOCK_DATA.showType
  )
  await userEvent.selectOptions(
    await screen.findByLabelText(LABELS.showSubType),
    MOCK_DATA.showSubType
  )

  await userEvent.selectOptions(
    await screen.findByLabelText(LABELS.musicType),
    MOCK_DATA.musicType
  )
}

describe('IndividualOfferDetails', () => {
  let contextValue: IndividualOfferContextValues

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock

    contextValue = individualOfferContextValuesFactory({
      categories: MOCK_DATA.categories,
      subCategories: MOCK_DATA.subCategories,
      offer: null,
    })
  })

  it('should render banner when no venue available', async () => {
    renderDetailsScreen({
      props: {
        venues: [],
      },
      contextValue,
    })

    expect(
      await screen.findByRole('heading', { name: 'À propos de votre offre' })
    ).toBeInTheDocument()
    expect(await screen.findByText(/Ajouter une structure/)).toBeInTheDocument()
  })

  it('should render the component', async () => {
    renderDetailsScreen({ contextValue })

    expect(
      await screen.findByRole('heading', { name: 'À propos de votre offre' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', { name: 'Illustrez votre offre' })
    ).toBeInTheDocument()
    expect(screen.getByText(DEFAULTS.submitButtonLabel)).toBeInTheDocument()
  })

  it('should display the full form when categories, and subcategories has been selected', async () => {
    renderDetailsScreen({ contextValue })
    const categoriesInput = await screen.findByLabelText('Catégorie *')
    expect(categoriesInput).toBeEnabled()
    await userEvent.selectOptions(categoriesInput, 'A')

    const subcategoriesInput = await screen.findByLabelText('Sous-catégorie *')
    expect(subcategoriesInput).toBeEnabled()
    await userEvent.selectOptions(subcategoriesInput, 'physical')

    expect(
      await screen.findByRole('heading', { name: 'Informations artistiques' })
    ).toBeInTheDocument()
  })

  it('should not display the venues list when venues is <= 1', () => {
    renderDetailsScreen({
      props: {
        venues: [venueListItemFactory({ id: 189 })],
      },
      contextValue,
    })

    expect(screen.queryByText(/Qui propose l’offre ?/)).not.toBeInTheDocument()
  })

  it('should show errors in the form when not all field has been filled', async () => {
    renderDetailsScreen({ contextValue })

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
      screen.getByText('Veuillez sélectionner une structure')
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

    renderDetailsScreen({ contextValue })

    await userEvent.type(
      screen.getByLabelText(/Titre de l’offre/),
      'My super offer'
    )
    await userEvent.type(
      screen.getByLabelText(/Description/),
      'My super description'
    )

    await userEvent.selectOptions(
      await screen.findByLabelText(/Qui propose l’offre ?/),
      '189'
    )

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
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
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

    renderDetailsScreen({ contextValue })
    await userFillsEverything()

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
      url: null,
    })
    expect(mockNavigate).toHaveBeenCalledWith(
      '/offre/individuelle/12/creation/details',
      { replace: true }
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
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
    contextValue.offer = getIndividualOfferFactory({
      id: 12,
      subcategoryId: 'physicalBis' as SubcategoryIdEnum,
    })

    renderDetailsScreen({ contextValue })

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
        ean: '1234567891234',
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
    it('should render an error when no selection has been made', async () => {
      renderDetailsScreen({ contextValue })

      // User selects fills the title.
      const titleInput = screen.getByLabelText(LABELS.title)
      await userEvent.type(titleInput, MOCK_DATA.title)

      // User doesn't select anything and submits.
      await userEvent.click(screen.getByText(DEFAULTS.submitButtonLabel))
      const error = screen.getByText('Veuillez sélectionner une catégorie')
      expect(error).toBeInTheDocument()
    })
  })

  it('should display first venue banner when venues are empty', () => {
    renderDetailsScreen({
      props: {
        venues: [],
      },
      contextValue,
    })
    expect(
      screen.getByText(
        'Pour créer une offre, vous devez d’abord créer une structure.'
      )
    ).toBeInTheDocument()
  })

  describe('on creation', () => {
    describe('about EAN search', () => {
      const eanSearchTitle = /Scanner ou rechercher un produit par EAN/
      const eanInputLabel = /Scanner ou rechercher un produit par EAN/
      const eanSearchButtonLabel = /Rechercher/
      const eanResetButtonLabel = /Effacer/
      it('should render EAN search for record stores as a venue', () => {
        const context = individualOfferContextValuesFactory({
          categories: MOCK_DATA.categories,
          subCategories: MOCK_DATA.subCategories,
          offer: null,
        })
        renderDetailsScreen({
          props: {
            venues: [
              venueListItemFactory({
                venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
              }),
            ],
          },
          contextValue: context,
          options: { features: ['WIP_EAN_CREATION'] },
          initialRoute:
            getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.DETAILS,
              mode: OFFER_WIZARD_MODE.CREATION,
            }) + '?offer-type=PHYSICAL_GOOD',
        })
        expect(screen.getByText(eanSearchTitle)).toBeInTheDocument()
      })

      it('should not render EAN search for other venues', () => {
        const context = individualOfferContextValuesFactory({
          categories: MOCK_DATA.categories,
          subCategories: MOCK_DATA.subCategories,
          offer: null,
        })
        renderDetailsScreen({
          props: {
            venues: [
              venueListItemFactory({
                venueTypeCode: VenueTypeCode.FESTIVAL,
              }),
            ],
          },
          contextValue: context,
          options: { features: ['WIP_EAN_CREATION'] },
          initialRoute:
            getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.DETAILS,
              mode: OFFER_WIZARD_MODE.CREATION,
            }) + '?offer-type=PHYSICAL_GOOD',
        })
        expect(screen.queryByText(eanSearchTitle)).not.toBeInTheDocument()
      })

      describe('when a local draft offer is being created', () => {
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
            categories: MOCK_DATA.categories,
            subCategories: MOCK_DATA.subCategories,
            offer: null,
          })
          vi.spyOn(api, 'getProductByEan').mockResolvedValue(productData)
          renderDetailsScreen({
            props: {
              venues: [
                venueListItemFactory({
                  venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
                }),
              ],
            },
            contextValue: context,
            options: { features: ['WIP_EAN_CREATION'] },
            initialRoute:
              getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.DETAILS,
                mode: OFFER_WIZARD_MODE.CREATION,
              }) + '?offer-type=PHYSICAL_GOOD',
          })
          const button = screen.getByRole('button', {
            name: eanSearchButtonLabel,
          })
          const input = screen.getByRole('textbox', { name: eanInputLabel })
          await userEvent.type(input, ean)
          await userEvent.click(button)
          // Inputs are filled with the product data and image is displayed.
          const nameInputLabel = /Titre de l’offre/
          const inputName = screen.getByRole('textbox', {
            name: nameInputLabel,
          })
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

        it('should reset the prefilled form when EAN search is cleared', async () => {
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
            categories: MOCK_DATA.categories,
            subCategories: MOCK_DATA.subCategories,
            offer: null,
          })
          vi.spyOn(api, 'getProductByEan').mockResolvedValue(productData)
          renderDetailsScreen({
            props: {
              venues: [
                venueListItemFactory({
                  venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
                }),
              ],
            },
            contextValue: context,
            options: { features: ['WIP_EAN_CREATION'] },
            initialRoute:
              getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.DETAILS,
                mode: OFFER_WIZARD_MODE.CREATION,
              }) + '?offer-type=PHYSICAL_GOOD',
          })
          const button = screen.getByRole('button', {
            name: eanSearchButtonLabel,
          })
          const input = screen.getByRole('textbox', { name: eanInputLabel })
          await userEvent.type(input, ean)
          await userEvent.click(button)
          const resetButton = screen.getByRole('button', {
            name: eanResetButtonLabel,
          })
          await userEvent.click(resetButton)
          // Inputs and image should be cleared.
          const nameInputLabel = /Titre de l’offre/
          const inputName = screen.getByRole('textbox', {
            name: nameInputLabel,
          })
          const image = screen.queryByTestId('image-preview')
          expect(inputName).toHaveValue('')
          expect(image).not.toBeInTheDocument()
        })

        it('should disabled all fields if another offer with the same EAN is already published', async () => {
          vi.spyOn(api, 'getActiveVenueOfferByEan').mockResolvedValueOnce({
            id: 1,
            dateCreated: '',
            isActive: true,
            name: 'test',
            status: OfferStatus.DRAFT,
            subcategoryId: SubcategoryIdEnum.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE,
          })
          const context = individualOfferContextValuesFactory({
            categories: MOCK_DATA.categories,
            subCategories: MOCK_DATA.subCategories,
            publishedOfferWithSameEAN: getIndividualOfferFactory({
              subcategoryId: SubcategoryIdEnum.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE,
            }),
            offer: getIndividualOfferFactory({
              subcategoryId:
                'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE' as SubcategoryIdEnum,
              productId: 1,
            }),
          })
          renderDetailsScreen({
            props: {
              venues: [
                venueListItemFactory({
                  venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
                }),
              ],
            },
            contextValue: context,
            options: { features: ['WIP_EAN_CREATION'] },
            initialRoute:
              getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.DETAILS,
                mode: OFFER_WIZARD_MODE.CREATION,
              }) + '?offer-type=PHYSICAL_GOOD',
          })

          await waitFor(() => {
            const inputName = screen.getByRole('textbox', {
              name: 'Titre de l’offre *',
            })
            expect(inputName).toBeDisabled()
          })
        })
      })

      describe('when the draft offer being created is no longer local but posted', () => {
        it('should render EAN search when the draft offer is product-based', async () => {
          const context = individualOfferContextValuesFactory({
            categories: MOCK_DATA.categories,
            subCategories: MOCK_DATA.subCategories,
            offer: getIndividualOfferFactory({
              subcategoryId:
                'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE' as SubcategoryIdEnum,
              productId: 1,
            }),
          })

          renderDetailsScreen({
            props: {
              venues: [
                venueListItemFactory({
                  venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
                }),
              ],
            },
            contextValue: context,
            options: { features: ['WIP_EAN_CREATION'] },
            initialRoute:
              getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.DETAILS,
                mode: OFFER_WIZARD_MODE.CREATION,
              }) + '?offer-type=PHYSICAL_GOOD',
          })
          await waitFor(() => {
            expect(screen.getByText(eanSearchTitle)).toBeInTheDocument()
          })
        })

        it('should not render EAN search when the draft offer is non product-based', () => {
          const context = individualOfferContextValuesFactory({
            categories: MOCK_DATA.categories,
            subCategories: MOCK_DATA.subCategories,
            offer: getIndividualOfferFactory({
              subcategoryId: 'physical' as SubcategoryIdEnum,
            }),
          })
          renderDetailsScreen({
            props: {
              venues: [
                venueListItemFactory({
                  venueTypeCode: 'RECORD_STORE' as VenueTypeCode,
                }),
              ],
            },
            contextValue: context,
            options: { features: ['WIP_EAN_CREATION'] },
            initialRoute:
              getIndividualOfferPath({
                step: OFFER_WIZARD_STEP_IDS.DETAILS,
                mode: OFFER_WIZARD_MODE.CREATION,
              }) + '?offer-type=PHYSICAL_GOOD',
          })
          expect(screen.queryByText(eanSearchTitle)).not.toBeInTheDocument()
        })
      })
    })
  })

  describe('on edition', () => {
    it('should not render EAN search', () => {
      const context = individualOfferContextValuesFactory({
        categories: MOCK_DATA.categories,
        subCategories: MOCK_DATA.subCategories,
        offer: getIndividualOfferFactory({
          subcategoryId: 'physical' as SubcategoryIdEnum,
        }),
      })

      renderDetailsScreen({
        contextValue: context,
        options: { features: ['WIP_EAN_CREATION'] },
        mode: OFFER_WIZARD_MODE.EDITION,
      })

      expect(
        screen.queryByText(/Scanner ou rechercher un produit par EAN/)
      ).not.toBeInTheDocument()
    })

    it('should display categories and subcategories as disabled', () => {
      const context = individualOfferContextValuesFactory({
        categories: MOCK_DATA.categories,
        subCategories: MOCK_DATA.subCategories,
        offer: getIndividualOfferFactory({
          subcategoryId: 'physical' as SubcategoryIdEnum,
        }),
      })

      renderDetailsScreen({
        contextValue: context,
        mode: OFFER_WIZARD_MODE.EDITION,
      })

      expect(screen.getByLabelText('Catégorie *')).toBeDisabled()
      expect(screen.getByLabelText('Sous-catégorie *')).toBeDisabled()
    })
  })

  it('should not render venue field when there is just one virtual venue', () => {
    renderDetailsScreen({
      props: {
        venues: [venueListItemFactory({ id: 189, isVirtual: true })],
      },
      contextValue,
    })

    expect(screen.queryByText(/Qui propose l’offre ?/)).not.toBeInTheDocument()
  })

  it('should not render venue field when there is just one physical venue', () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      SUGGESTED_CATEGORIES: 'true',
    })

    renderDetailsScreen({
      props: {
        venues: [venueListItemFactory({ id: 189, isVirtual: false })],
      },
      contextValue,
    })

    expect(screen.queryByText(/Qui propose l’offre ?/)).not.toBeInTheDocument()
  })

  it('should not render venue field when there is one physical venue and one virtual venue', () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      SUGGESTED_CATEGORIES: 'true',
    })

    renderDetailsScreen({
      props: {
        venues: [
          venueListItemFactory({ id: 189, isVirtual: false }),
          venueListItemFactory({ id: 190, isVirtual: true }),
        ],
      },
      contextValue,
    })

    expect(screen.queryByText(/Qui propose l’offre ?/)).not.toBeInTheDocument()
  })

  describe('onboarding', () => {
    beforeEach(() => {
      vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    })

    it('should display with the lateral bar', async () => {
      renderDetailsScreen({
        props: {
          venues: [venueListItemFactory({ id: 189 })],
        },
        contextValue,
      })
      await userEvent.click(screen.getByText('Retour'))
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/offre/creation')
      })
    })

    it('should not render when the offer is not set', async () => {
      renderDetailsScreen({
        props: {
          venues: [venueListItemFactory({ id: 189 })],
        },
        contextValue,
        options: {},
        mode: OFFER_WIZARD_MODE.CREATION,
        initialRoute: `/onboarding${getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}`,
      })
      await userEvent.click(screen.getByText('Retour'))
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/onboarding/offre/creation')
      })
    })
  })
})
