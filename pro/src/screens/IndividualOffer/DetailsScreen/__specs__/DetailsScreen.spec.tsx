import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
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

import { DetailsScreen, DetailsScreenProps } from '../DetailsScreen'

vi.mock('apiClient/api', () => ({
  api: {
    getMusicTypes: vi.fn(),
    postDraftOffer: vi.fn(),
    getSuggestedSubcategories: vi.fn(),
  },
}))

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

const scrollIntoViewMock = vi.fn()

const renderDetailsScreen = (
  props: DetailsScreenProps,
  contextValue: IndividualOfferContextValues,
  options: RenderWithProvidersOptions = {}
) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsScreen {...props} />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('screens:IndividualOffer::Informations', () => {
  let props: DetailsScreenProps
  let contextValue: IndividualOfferContextValues

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const categories = [
      categoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
    ]
    const subCategories = [
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: ['author'],
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

  it('should render the component', async () => {
    renderDetailsScreen(props, contextValue)

    expect(
      await screen.findByRole('heading', { name: 'A propos de votre offre' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
    expect(screen.getByText('Annuler et quitter')).toBeInTheDocument()
    expect(
      screen.getByText('Enregistrer les modifications')
    ).toBeInTheDocument()
  })

  it('should display the full form when categories, and subcategories has been selected', async () => {
    renderDetailsScreen(props, contextValue)
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

  it('should show errors in the form when not all field has been filled', async () => {
    renderDetailsScreen(props, contextValue)

    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(
      screen.getByText('Veuillez sélectionner une catégorie')
    ).toBeInTheDocument()

    await userEvent.selectOptions(
      await screen.findByLabelText('Catégorie *'),
      'A'
    )
    await userEvent.click(screen.getByText('Enregistrer les modifications'))
    expect(
      screen.getByText('Veuillez sélectionner une sous-catégorie')
    ).toBeInTheDocument()

    await userEvent.selectOptions(
      await screen.findByLabelText('Sous-catégorie *'),
      'physical'
    )

    await userEvent.click(screen.getByText('Enregistrer les modifications'))
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
    vi.spyOn(api, 'postDraftOffer').mockResolvedValue(
      getIndividualOfferFactory({
        id: 12,
      })
    )
    vi.spyOn(api, 'getMusicTypes').mockResolvedValue([
      { canBeEvent: true, label: 'Pop', gtl_id: 'pop' },
    ])
    props.venues = [venueListItemFactory({ id: 189 })]

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

    await userEvent.click(screen.getByText('Enregistrer les modifications'))

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
  })

  it('should render suggested subcategories', async () => {
    vi.spyOn(api, 'getSuggestedSubcategories').mockResolvedValue({
      subcategoryIds: ['virtual', 'physical'],
    })

    renderDetailsScreen(props, contextValue, {
      features: ['WIP_SUGGESTED_SUBCATEGORIES'],
    })

    // at first there is no suggested subcategories
    expect(
      screen.queryByText(/Catégories suggérées pour votre offre/)
    ).not.toBeInTheDocument()

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

    await userEvent.click(screen.getByText('Sous catégorie offline de A'))
    expect(screen.queryByText('Auteur')).not.toBeInTheDocument()
    expect(screen.getByText(/EAN/)).toBeInTheDocument()

    // When clicking on "Autre", we can choose subcategory and the conditional fields are hidden
    await userEvent.click(screen.getByText('Autre'))
    expect(screen.queryByText('Auteur')).not.toBeInTheDocument()
    expect(screen.queryByText(/EAN/)).not.toBeInTheDocument()
    expect(screen.getByLabelText(/Catégorie/)).toBeInTheDocument()
  })
})
