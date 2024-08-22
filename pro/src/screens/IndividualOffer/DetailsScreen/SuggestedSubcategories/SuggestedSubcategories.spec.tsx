import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormikProvider, useFormik } from 'formik'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { subcategoryFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  SuggestedSubcategories,
  SuggestedSubcategoriesProps,
} from './SuggestedSubcategories'

const CATEGORIES: CategoryResponseModel[] = [
  {
    id: 'LIVRE',
    isSelectable: true,
    proLabel: 'Livre',
  },
  {
    id: 'SPECTACLE',
    isSelectable: true,
    proLabel: 'Spectacle',
  },
  {
    id: 'FILM',
    isSelectable: true,
    proLabel: 'Film',
  },
  {
    id: 'INSTRUMENT',
    isSelectable: true,
    proLabel: 'Instrument',
  },
]

const SUB_CATEGORIES: SubcategoryResponseModel[] = [
  subcategoryFactory({
    id: 'LIVRE_PAPIER',
    categoryId: 'LIVRE',
    proLabel: 'Livre papier',
    conditionalFields: ['author', 'ean', 'gtl_id'],
  }),
  subcategoryFactory({
    id: 'SPECTACLE_REPRESENTATION',
    categoryId: 'SPECTACLE',
    proLabel: 'Spectacle, représentation',
    conditionalFields: [
      'author',
      'showSubType',
      'showType',
      'stageDirector',
      'performer',
    ],
  }),
  subcategoryFactory({
    id: 'ABO_PLATEFORME_VIDEO',
    categoryId: 'FILM',
    proLabel: 'Abonnement plateforme streaming',
    conditionalFields: [],
  }),
  subcategoryFactory({
    id: 'BON_ACHAT_INSTRUMENT',
    categoryId: 'INSTRUMENT',
    proLabel: "Bon d'achat instrument",
    conditionalFields: [],
  }),
]

const suggestedSubcategories = SUB_CATEGORIES.map((subcat) => subcat.id)
const firstSuggestedSubcategories = suggestedSubcategories.slice(0, 2)
const otherSuggestedSubcategories = suggestedSubcategories.slice(2)

const contextValue: IndividualOfferContextValues = {
  categories: [],
  subCategories: SUB_CATEGORIES,
  offer: null,
}
const SuggestedSubWrappedWithFormik = (
  props: SuggestedSubcategoriesProps
): JSX.Element => {
  const formik = useFormik({
    initialValues: {
      categoryId: '',
      subcategoryConditionalFields: [],
      suggestedSubcategory: '',
    },
    onSubmit: vi.fn(),
  })

  return (
    <FormikProvider value={formik}>
      <SuggestedSubcategories {...props} />
    </FormikProvider>
  )
}

const renderSuggestedSubcategories = (props: SuggestedSubcategoriesProps) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <SuggestedSubWrappedWithFormik {...props} />
    </IndividualOfferContext.Provider>,
    {}
  )
}

describe('SuggestedSubcategories', () => {
  it('should render suggested subcategories as radio buttons', () => {
    renderSuggestedSubcategories({
      suggestedSubcategories,
      filteredCategories: [],
      filteredSubcategories: [],
      readOnlyFields: [],
    })

    suggestedSubcategories.forEach((subcategoryId, index) => {
      const label = SUB_CATEGORIES[index].proLabel
      const radioButton = screen.queryByRole('radio', { name: label })
      expect(radioButton).toBeInTheDocument()
    })
  })

  it('should always render an "Autre" radio button', () => {
    renderSuggestedSubcategories({
      suggestedSubcategories,
      filteredCategories: [],
      filteredSubcategories: [],
      readOnlyFields: [],
    })

    const radioButton = screen.queryByRole('radio', { name: 'Autre' })
    expect(radioButton).toBeInTheDocument()
  })

  it('should keep previously selected subcategory as radio button even if it is not in the suggested subcategories', async () => {
    const { rerender } = renderSuggestedSubcategories({
      suggestedSubcategories: firstSuggestedSubcategories,
      filteredCategories: [],
      filteredSubcategories: [],
      readOnlyFields: [],
    })

    const selectedIndex = 0
    const selectedName = SUB_CATEGORIES[selectedIndex].proLabel
    const queryParams = { name: selectedName }

    const selected = screen.getByRole('radio', queryParams)
    await userEvent.click(selected)

    rerender(
      <IndividualOfferContext.Provider value={{ ...contextValue }}>
        <SuggestedSubWrappedWithFormik
          suggestedSubcategories={otherSuggestedSubcategories}
          filteredCategories={[]}
          filteredSubcategories={[]}
          readOnlyFields={[]}
        />
      </IndividualOfferContext.Provider>
    )

    // Previous suggested subcategories are no longer rendered
    // except previously selected.
    firstSuggestedSubcategories.forEach((subcategoryId, index) => {
      const label = SUB_CATEGORIES[index].proLabel
      const radioButton = screen.queryByRole('radio', { name: label })

      if (index === selectedIndex) {
        expect(radioButton).toBeInTheDocument()
      } else {
        expect(radioButton).not.toBeInTheDocument()
      }
    })
  })

  describe('when the "Autre" radio button is selected', () => {
    it('should render a category select', async () => {
      renderSuggestedSubcategories({
        suggestedSubcategories,
        filteredCategories: [],
        filteredSubcategories: [],
        readOnlyFields: [],
      })

      const otherRadioButton = screen.getByRole('radio', { name: 'Autre' })
      await userEvent.click(otherRadioButton)

      const categorySelect = screen.getByRole('combobox', {
        name: 'Catégorie *',
      })
      expect(categorySelect).toBeInTheDocument()
    })

    it('should render a subcategory select when a category is selected', async () => {
      renderSuggestedSubcategories({
        suggestedSubcategories,
        filteredCategories: CATEGORIES,
        filteredSubcategories: SUB_CATEGORIES,
        readOnlyFields: [],
      })

      const otherRadioButton = screen.getByRole('radio', { name: 'Autre' })
      await userEvent.click(otherRadioButton)

      const categorySelect = screen.getByRole('combobox', {
        name: 'Catégorie *',
      })
      await userEvent.selectOptions(categorySelect, 'LIVRE')

      const subcategorySelect = screen.getByRole('combobox', {
        name: 'Sous-catégorie *',
      })
      expect(subcategorySelect).toBeInTheDocument()
    })
  })
})
