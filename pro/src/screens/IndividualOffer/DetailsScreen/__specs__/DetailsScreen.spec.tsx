import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  categoryFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DetailsScreen, DetailsScreenProps } from '../DetailsScreen'

vi.mock('apiClient/api', () => ({
  api: {
    getMusicTypes: vi.fn(),
  },
}))

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

const scrollIntoViewMock = vi.fn()

const renderDetailsScreen = (
  props: DetailsScreenProps,
  contextValue: IndividualOfferContextValues
) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsScreen {...props} />
    </IndividualOfferContext.Provider>
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
})
