import '@testing-library/jest-dom'
import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  categoriesFactory,
  defaultCreationProps,
  elements,
  renderEACOfferForm,
  subCategoriesFactory,
  triggerFieldValidation,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

const {
  findOfferTypeTitle,
  queryOfferTypeTitle,
  queryCategorySelect,
  querySubcategorySelect,
  queryTitleInput,
  queryDescriptionTextArea,
  queryDurationInput,
} = elements
describe('screens | OfferEducational : creation offer type step', () => {
  let props: IOfferEducationalProps

  beforeEach(() => {
    props = defaultCreationProps
  })

  it('should display the right fields and titles', async () => {
    renderEACOfferForm(props)
    await findOfferTypeTitle()
    expect(queryOfferTypeTitle()).toBeInTheDocument()

    const categorySelect = queryCategorySelect()
    expect(categorySelect.input).toBeInTheDocument()
    expect(categorySelect.input).toBeEnabled()
    expect(categorySelect.input).toHaveValue('')
    expect(categorySelect.isOptionnal).toBe(false)

    const subCategorySelect = querySubcategorySelect()
    expect(subCategorySelect.input).not.toBeInTheDocument()

    const titleInput = queryTitleInput()
    expect(titleInput.input).toBeInTheDocument()
    expect(titleInput.input).toBeEnabled()
    expect(titleInput.input).toHaveValue('')
    expect(titleInput.isOptionnal).toBe(false)
    expect(titleInput.input?.placeholder).toMatchInlineSnapshot(`""`)

    const titleCharCounter = titleInput.getCounter()
    expect(titleCharCounter).toBeInTheDocument()
    expect(titleCharCounter).toHaveTextContent('0/90')

    const descriptionTextArea = queryDescriptionTextArea()
    expect(descriptionTextArea.input).toBeInTheDocument()
    expect(descriptionTextArea.input).toBeEnabled()
    expect(descriptionTextArea.input).toHaveValue('')
    expect(descriptionTextArea.input?.placeholder).toBe(
      'Détaillez ici votre projet et son interêt pédagogique'
    )
    expect(descriptionTextArea.isOptionnal).toBe(true)

    const descriptionCharCounter = descriptionTextArea.getCounter()
    expect(descriptionCharCounter).toBeInTheDocument()
    expect(descriptionCharCounter).toHaveTextContent('0/1000')

    const durationInput = queryDurationInput()
    expect(durationInput.input).toBeInTheDocument()
    expect(durationInput.input).toBeEnabled()
    expect(durationInput.input).toHaveValue('')
    expect(durationInput.input?.placeholder).toBe('HH:MM')
    expect(durationInput.isOptionnal).toBe(true)
  })

  describe('catégories and sub catégories', () => {
    beforeEach(() => {
      props = {
        ...props,
        educationalCategories: categoriesFactory([
          { id: 'CAT_1' },
          { id: 'CAT_2' },
        ]),
        educationalSubCategories: subCategoriesFactory([
          { categoryId: 'CAT_1', id: 'SUBCAT_1' },
          { categoryId: 'CAT_1', id: 'SUBCAT_2' },
          { categoryId: 'CAT_2', id: 'SUBCAT_3' },
          { categoryId: 'CAT_2', id: 'SUBCAT_4' },
        ]),
      }
    })
    it('should require user to select a category before displaying subcatégories', async () => {
      renderEACOfferForm(props)
      await findOfferTypeTitle()

      const categorySelect = queryCategorySelect()
      expect(categorySelect.input).toBeInTheDocument()

      expect(querySubcategorySelect().input).not.toBeInTheDocument()

      triggerFieldValidation(categorySelect.input as HTMLSelectElement)

      await waitFor(() => expect(categorySelect.getError()).toBeInTheDocument())
      expect(categorySelect.getError()).toHaveTextContent(
        'Veuillez sélectionner une catégorie'
      )

      userEvent.selectOptions(
        categorySelect.input as HTMLSelectElement,
        'CAT_1'
      )

      await waitFor(() =>
        expect(querySubcategorySelect().input).toBeInTheDocument()
      )

      expect(categorySelect.getError()).not.toBeInTheDocument()

      const subCategorySelect = querySubcategorySelect()
      expect(subCategorySelect.input?.options).toHaveLength(3)
      expect(subCategorySelect.input?.options[0].value).toBe('')
      expect(subCategorySelect.input?.options[1].value).toBe('SUBCAT_1')
      expect(subCategorySelect.input?.options[2].value).toBe('SUBCAT_2')
      expect(subCategorySelect.isOptionnal).toBe(false)
    })

    it('should require user to select a subcategory', async () => {
      renderEACOfferForm(props)
      await findOfferTypeTitle()
      const categorySelect = queryCategorySelect()
      userEvent.selectOptions(
        categorySelect.input as HTMLSelectElement,
        'CAT_1'
      )

      await waitFor(() =>
        expect(querySubcategorySelect().input).toBeInTheDocument()
      )

      const subCategorySelect = querySubcategorySelect()

      triggerFieldValidation(subCategorySelect.input as HTMLSelectElement)

      await waitFor(() =>
        expect(subCategorySelect.getError()).toBeInTheDocument()
      )
      expect(subCategorySelect.getError()).toHaveTextContent(
        'Veuillez sélectionner une sous-catégorie'
      )

      userEvent.selectOptions(
        subCategorySelect.input as HTMLSelectElement,
        'SUBCAT_1'
      )

      await waitFor(() =>
        expect(subCategorySelect.getError()).not.toBeInTheDocument()
      )
    })
  })
  describe('catégories and sub catégories / when there is only one item', () => {
    beforeEach(() => {
      props = {
        ...props,
        educationalCategories: categoriesFactory([
          { id: 'CAT_1', label: 'cat 1' },
        ]),
        educationalSubCategories: subCategoriesFactory([
          { categoryId: 'CAT_1', id: 'SUBCAT_1', label: 'subcat 1' },
        ]),
      }
    })
    it('should pre-select both categories and subcategories', async () => {
      renderEACOfferForm(props)
      await findOfferTypeTitle()

      const categorySelect = queryCategorySelect()
      const subCategorySelect = querySubcategorySelect()

      expect(categorySelect.input).toBeInTheDocument()
      expect(subCategorySelect.input).toBeInTheDocument()

      expect(categorySelect.input?.options).toHaveLength(1)
      expect(subCategorySelect.input?.options).toHaveLength(1)

      expect(categorySelect.input).toHaveValue('CAT_1')
      expect(subCategorySelect.input).toHaveValue('SUBCAT_1')
    })
  })
})
