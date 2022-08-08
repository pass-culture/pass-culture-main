import '@testing-library/jest-dom'

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  categoriesFactory,
  defaultCreationProps,
  renderEACOfferForm,
  subCategoriesFactory,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : creation offer type step', () => {
  let props: IOfferEducationalProps
  let store: any

  beforeEach(() => {
    props = defaultCreationProps
  })

  it('should display the right fields and titles', async () => {
    renderEACOfferForm(props)

    const categorySelect = await screen.findByLabelText('Catégorie')
    expect(categorySelect).toBeInTheDocument()
    expect(categorySelect).toBeEnabled()
    expect(categorySelect).toHaveValue('')

    expect(screen.queryByLabelText('Sous-catégorie')).not.toBeInTheDocument()

    const titleInput = await screen.findByLabelText('Titre de l’offre')
    expect(titleInput).toBeEnabled()
    expect(titleInput).toHaveValue('')
    expect(titleInput.getAttribute('placeholder')).toBeNull()

    expect(await screen.findByTestId('counter-title')).toHaveTextContent('0/90')

    const descriptionTextArea = await screen.findByLabelText(/Description/)
    expect(descriptionTextArea).toBeEnabled()
    expect(descriptionTextArea).toHaveValue('')
    expect(descriptionTextArea.getAttribute('placeholder')).toBe(
      'Détaillez ici votre projet et son interêt pédagogique'
    )
    expect(await screen.findByTestId('counter-description')).toHaveTextContent(
      '0/1000'
    )

    const durationInput = screen.getByLabelText(/Durée/)
    expect(durationInput).toBeInTheDocument()
    expect(durationInput).toBeEnabled()
    expect(durationInput).toHaveValue('')
    expect(durationInput.getAttribute('placeholder')).toBe('HH:MM')
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

      const categorySelect = await screen.findByLabelText('Catégorie')
      expect(categorySelect).toBeInTheDocument()

      expect(screen.queryByLabelText('Sous-catégorie')).not.toBeInTheDocument()

      await userEvent.click(categorySelect)
      await userEvent.tab()

      expect(
        await screen.findByText('Veuillez sélectionner une catégorie')
      ).toBeInTheDocument()

      await userEvent.selectOptions(categorySelect, 'CAT_1')

      expect(await screen.findByLabelText('Sous-catégorie')).toBeInTheDocument()

      expect(
        screen.queryByText('Veuillez sélectionner une catégorie')
      ).not.toBeInTheDocument()

      const subCategorySelect = screen.getByLabelText('Sous-catégorie')
      expect(subCategorySelect.children).toHaveLength(3)
      expect(subCategorySelect.children[0]).toHaveValue('')
      expect(subCategorySelect.children[1]).toHaveValue('SUBCAT_1')
      expect(subCategorySelect.children[2]).toHaveValue('SUBCAT_2')
    })

    it('should require user to select a subcategory', async () => {
      renderEACOfferForm(props)
      const categorySelect = await screen.findByLabelText('Catégorie')
      await userEvent.selectOptions(categorySelect, 'CAT_1')

      await waitFor(() =>
        expect(screen.getByLabelText('Sous-catégorie')).toBeInTheDocument()
      )

      const subCategorySelect = screen.getByLabelText('Sous-catégorie')

      await userEvent.click(subCategorySelect)
      await userEvent.tab()

      expect(
        screen.getByText('Veuillez sélectionner une sous-catégorie')
      ).toBeInTheDocument()

      await userEvent.selectOptions(subCategorySelect, 'SUBCAT_1')

      expect(
        screen.queryByText('Veuillez sélectionner une sous-catégorie')
      ).not.toBeInTheDocument()
    })
  })
  describe('domains', () => {
    beforeEach(() => {
      props = {
        ...props,
        getEducationalDomainsAdapter: jest.fn().mockResolvedValue({
          payload: [
            { label: 'Domain 1', value: '1' },
            { label: 'Domain 2', value: '2' },
            { label: 'Domain 3', value: '3' },
          ],
        }),
      }
    })

    it('should require user to select a domain', async () => {
      renderEACOfferForm(props, store)

      await userEvent.click(
        await screen.findByLabelText(/Domaine artistique et culturel/)
      )

      await userEvent.click(screen.getByLabelText(/Catégorie/))

      expect(
        screen.getByText('Veuillez renseigner un domaine')
      ).toBeInTheDocument()
    })

    it('should enable user to select domains', async () => {
      renderEACOfferForm(props, store)

      await userEvent.click(
        await screen.findByLabelText(/Domaine artistique et culturel/)
      )

      await userEvent.click(await screen.findByLabelText(/Domain 2/))

      await userEvent.click(screen.getByLabelText(/Catégorie/))

      expect(
        screen.queryByText('Veuillez renseigner un domaine')
      ).not.toBeInTheDocument()
    })
  })

  describe('title, description and duration inputs', () => {
    it('should require a title with less than 90 chars (and truncate longer strings)', async () => {
      renderEACOfferForm(props)

      const titleMaxLength = 90

      const titleInput = await screen.findByLabelText('Titre de l’offre')
      expect(titleInput).toHaveValue('')
      expect(screen.getByTestId('counter-title')).toHaveTextContent(
        `0/${titleMaxLength}`
      )

      await userEvent.click(titleInput)
      await userEvent.tab()

      await waitFor(() =>
        expect(
          screen.getByText('Veuillez renseigner un titre')
        ).toBeInTheDocument()
      )

      const title =
        'a valid title ' + Array.from({ length: 50 }).map(() => 'test ')
      await userEvent.type(titleInput, title)

      expect(screen.getByTestId('counter-title')).toHaveTextContent(
        `${titleMaxLength}/${titleMaxLength}`
      )

      await expect(titleInput.getAttribute('value')).toHaveLength(
        titleMaxLength
      )
    })

    it('should require a description with less than 1000 chars (and truncate longer strings)', async () => {
      renderEACOfferForm(props)

      const descMaxLength = 1000

      const description = await screen.findByLabelText(/Description/)
      expect(description).toHaveValue('')
      expect(screen.getByTestId('counter-description')).toHaveTextContent(
        `0/${descMaxLength}`
      )

      const descriptionString =
        'my description that is valid' +
        Array.from({ length: 50 }).map(() => 'description pour tester')

      // hack - to be fixed
      await userEvent.click(description)
      await userEvent.paste(descriptionString)

      expect(descriptionString).toContain(description.textContent)

      expect(screen.getByTestId('counter-description')).toHaveTextContent(
        `${descMaxLength}/${descMaxLength}`
      )

      await expect(description.textContent).toHaveLength(descMaxLength)
    })

    it('should have a duration field with a format of hh:mm', async () => {
      renderEACOfferForm(props)

      const duration = await screen.findByLabelText(/Durée/)
      expect(duration).toHaveValue('')

      await userEvent.type(duration, 'bad String')

      await waitFor(() => expect(duration).toHaveValue('bad String'))

      await userEvent.click(duration)
      await userEvent.tab()

      expect(
        screen.getByText(
          'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
        )
      ).toBeInTheDocument()

      await userEvent.clear(duration)
      await userEvent.type(duration, '2:30')

      expect(duration).toHaveValue('2:30')

      expect(
        screen.queryByText(
          'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
        )
      ).not.toBeInTheDocument()
    })
  })
})
