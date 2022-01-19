import '@testing-library/jest-dom'
import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { triggerFieldValidation } from 'ui-kit/form/__tests-utils__'

import {
  categoriesFactory,
  defaultCreationProps,
  elements,
  renderEACOfferForm,
  subCategoriesFactory,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

const {
  findOfferTypeTitle,
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
    it('should require user to select a category before displaying subcategories', async () => {
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

  describe('title, description and duration inputs', () => {
    it('should require a title with less than 90 chars (and truncate longer strings)', async () => {
      renderEACOfferForm(props)
      await findOfferTypeTitle()

      const titleMaxLength = 90

      const titleInput = queryTitleInput()
      expect(titleInput.input).toHaveValue('')
      expect(titleInput.getCounter()).toHaveTextContent(`0/${titleMaxLength}`)

      triggerFieldValidation(titleInput.input as HTMLInputElement)

      await waitFor(() => expect(titleInput.getError()).toBeInTheDocument())

      expect(titleInput.getError()).toHaveTextContent(
        'Veuillez renseigner un titre'
      )

      const title = 'a valid title'
      userEvent.paste(titleInput.input as HTMLInputElement, title)

      await waitFor(() => expect(titleInput.getError()).not.toBeInTheDocument())
      expect(titleInput.getCounter()).toHaveTextContent(
        `${title.length}/${titleMaxLength}`
      )

      await expect(titleInput.doesTruncateAt(titleMaxLength)).resolves.toBe(
        true
      )
    })

    it('should require a description with less than 1000 chars (and truncate longer strings)', async () => {
      renderEACOfferForm(props)
      await findOfferTypeTitle()

      const descMaxLength = 1000

      const description = queryDescriptionTextArea()
      expect(description.input).toHaveValue('')
      expect(description.getCounter()).toHaveTextContent(`0/${descMaxLength}`)

      const descriptionString = 'my description that is valid'

      userEvent.paste(
        description.input as HTMLTextAreaElement,
        descriptionString
      )

      await waitFor(() =>
        expect(description.input).toHaveValue(descriptionString)
      )

      expect(description.getCounter()).toHaveTextContent(
        `${descriptionString.length}/${descMaxLength}`
      )

      await expect(description.doesTruncateAt(descMaxLength)).resolves.toBe(
        true
      )
    })

    it('should have a duration field with a format of hh:mm', async () => {
      renderEACOfferForm(props)
      await findOfferTypeTitle()

      const duration = queryDurationInput()
      expect(duration.input).toHaveValue('')

      userEvent.paste(duration.input as HTMLInputElement, 'bad String')

      await waitFor(() => expect(duration.input).toHaveValue('bad String'))

      triggerFieldValidation(duration.input as HTMLInputElement)

      await waitFor(() =>
        expect(duration.getError()).toHaveTextContent(
          'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
        )
      )

      userEvent.clear(duration.input as HTMLInputElement)
      userEvent.paste(duration.input as HTMLInputElement, '2:30')

      await waitFor(() => expect(duration.input).toHaveValue('2:30'))
      await waitFor(() => expect(duration.getError()).not.toBeInTheDocument())
    })
  })
})
