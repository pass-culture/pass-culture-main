import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import * as yup from 'yup'

import { api } from 'apiClient/api'
import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'
import { Button } from 'ui-kit/Button/Button'
import {
  categoryFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Categories, CategoriesProps } from '../Categories'
import { CATEGORIES_DEFAULT_VALUES } from '../constants'
import { getValidationSchema } from '../validationSchema'

const renderCategories = ({
  initialValues,
  onSubmit,
  props,
}: {
  initialValues: Partial<IndividualOfferFormValues>
  onSubmit: () => void
  props: CategoriesProps
  contextOverride?: Partial<IndividualOfferContextValues>
}) => {
  const contextValues = individualOfferContextValuesFactory()
  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={yup.object().shape(getValidationSchema(true))}
      >
        <Form>
          <Categories {...props} />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </Form>
      </Formik>
    </IndividualOfferContext.Provider>,
    { features: ['ENABLE_PRO_TITELIVE_MUSIC_GENRES'] }
  )
}

describe('IndividualOffer section: Categories', () => {
  let initialValues: Partial<IndividualOfferFormValues>
  const onSubmit = vi.fn()
  let props: CategoriesProps
  let categories: CategoryResponseModel[] = []
  let subCategories: SubcategoryResponseModel[] = []

  beforeEach(() => {
    initialValues = { ...CATEGORIES_DEFAULT_VALUES }
    categories = [
      categoryFactory({ id: 'A' }),
      categoryFactory({ id: 'B' }),
      categoryFactory({ id: 'C' }),
    ]
    subCategories = [
      subcategoryFactory({
        id: 'A-A',
        categoryId: 'A',
      }),
      subcategoryFactory({
        id: 'B-A',
        categoryId: 'B',
        conditionalFields: ['gtl_id'],
      }),
      subcategoryFactory({
        id: 'C-A',
        categoryId: 'C',
        conditionalFields: ['showType', 'showSubType'],
      }),
    ]
    props = {
      categories,
      subCategories,
      offerSubtype: INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
      venueList: [],
      isEvent: true,
      showAddVenueBanner: true,
    }
  })

  it('should render the component', () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    expect(screen.getByLabelText('Catégorie *')).toBeInTheDocument()
    const infoBox = screen.getByText(
      'Une sélection précise de vos catégories permettra au grand public de facilement trouver votre offre. Une fois validées, vous ne pourrez pas les modifier.'
    )
    const infoLink = screen.getByText('Quelles catégories choisir ?')
    expect(infoBox).toBeInTheDocument()
    expect(infoLink).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-'
    )
  })

  it('should submit valid form', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'C-A')
    const showSelect = screen.getByLabelText('Type de spectacle *')
    await userEvent.selectOptions(showSelect, '100')
    const subShowSelect = screen.getByLabelText('Sous-type *')
    await userEvent.selectOptions(subShowSelect, '101')

    await userEvent.click(screen.getByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        author: '',
        categoryId: 'C',
        durationMinutes: '',
        isEvent: false,
        ean: '',
        gtl_id: '',
        musicType: '',
        musicSubType: '',
        performer: '',
        showSubType: '101',
        showType: '100',
        speaker: '',
        stageDirector: '',
        subCategoryFields: ['showType', 'showSubType'],
        subcategoryId: 'C-A',
        visa: '',
        isDuo: false,
        withdrawalDelay: undefined,
        withdrawalType: undefined,
      },
      expect.anything()
    )
  })

  it('should display subCategories select when a category is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    expect(screen.getByLabelText('Sous-catégorie *')).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Type de spectacle *')
    ).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type *')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Genre musical *')).not.toBeInTheDocument()
  })

  it('should not display type select when a standard subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'A-A')

    expect(screen.getByLabelText('Sous-catégorie *')).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Type de spectacle *')
    ).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type *')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Genre musical *')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-genre *')).not.toBeInTheDocument()
  })

  it('should display music genre selects when a music subCategory is chosen', async () => {
    const musicTypeSpy = vi.spyOn(api, 'getMusicTypes').mockResolvedValue([
      {
        gtl_id: '07000000',
        label: 'Metal',
        canBeEvent: true,
      },
    ])

    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'B')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'B-A')

    expect(screen.queryByLabelText('Sous-genre *')).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Type de spectacle *')
    ).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type *')).not.toBeInTheDocument()

    const musicSelect = screen.getByLabelText('Genre musical *')
    expect(musicSelect).toBeInTheDocument()

    await waitFor(() => {
      return expect(musicTypeSpy).toHaveBeenCalled()
    })

    await userEvent.selectOptions(musicSelect, '07000000')

    expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()
  })

  it('should display showType selects when a music subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'C-A')

    expect(screen.queryByLabelText('Genre musical')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()

    const showSelect = screen.getByLabelText('Type de spectacle *')
    expect(showSelect).toBeInTheDocument()

    await userEvent.selectOptions(showSelect, '100')
    expect(screen.getByLabelText('Sous-type *')).toBeInTheDocument()

    expect(screen.queryByLabelText('Genre musical *')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-genre *')).not.toBeInTheDocument()
  })

  it('should not display subType selects when a music category is back to default', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'C-A')

    const showSelect = screen.getByLabelText('Type de spectacle *')
    expect(showSelect).toBeInTheDocument()

    await userEvent.selectOptions(showSelect, '100')
    expect(screen.getByLabelText('Sous-type *')).toBeInTheDocument()

    await userEvent.selectOptions(categorySelect, '')
    expect(
      screen.queryByLabelText('Type de spectacle *')
    ).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type *')).not.toBeInTheDocument()
  })
})
