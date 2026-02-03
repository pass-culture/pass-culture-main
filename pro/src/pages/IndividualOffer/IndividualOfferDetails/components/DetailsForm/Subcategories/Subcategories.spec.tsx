import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useEffect } from 'react'
import { FormProvider, type UseFormReturn, useForm } from 'react-hook-form'

import {
  categoryFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'

import { Subcategories } from './Subcategories'

const categories = [
  categoryFactory({ id: 'A', proLabel: 'Catégorie A', isSelectable: true }),
]

const subcategories = [
  subcategoryFactory({
    id: 'sub-A',
    categoryId: 'A',
    proLabel: 'Sous-catégorie A1',
    conditionalFields: ['author', 'speaker', 'ean'],
  }),
  subcategoryFactory({
    id: 'sub-A2',
    categoryId: 'A',
    proLabel: 'Sous-catégorie A2',
  }),
]

const SubcategoriesForm = ({
  readOnlyFields = [],
  onReady,
}: {
  readOnlyFields?: string[]
  onReady?: (methods: UseFormReturn<DetailsFormValues>) => void
}) => {
  const methods = useForm<DetailsFormValues>({
    defaultValues: {
      ...DEFAULT_DETAILS_FORM_VALUES,
    },
  })

  const conditionalFields = methods.watch('subcategoryConditionalFields')

  // biome-ignore lint/correctness/useExhaustiveDependencies: This is a test.
  useEffect(() => {
    onReady?.(methods)
  }, [])

  return (
    <FormProvider {...methods}>
      <Subcategories
        readOnlyFields={readOnlyFields}
        filteredCategories={categories}
        filteredSubcategories={subcategories}
      />
      {conditionalFields.map((field) => (
        <input key={field} {...methods.register(field)} />
      ))}
    </FormProvider>
  )
}

const renderSubCategories = (options?: {
  readOnlyFields?: string[]
  onReady?: (actions: UseFormReturn<DetailsFormValues>) => void
}) => {
  return render(<SubcategoriesForm {...options} />)
}

describe('<Subcategories />', () => {
  it('renders the category select', () => {
    renderSubCategories()
    expect(screen.getByLabelText(/Catégorie/)).toBeInTheDocument()
  })

  it('renders subcategory select only after selecting a category', async () => {
    renderSubCategories()

    expect(screen.queryByLabelText(/Sous-catégorie/)).not.toBeInTheDocument()

    const categorySelect = screen.getByLabelText(/Catégorie/)
    await userEvent.selectOptions(categorySelect, 'A')

    expect(await screen.findByLabelText(/Sous-catégorie/)).toBeInTheDocument()
  })

  it('disables selects when readOnlyFields is set', () => {
    renderSubCategories({ readOnlyFields: ['categoryId', 'subcategoryId'] })
    expect(screen.getByLabelText(/Catégorie/)).toBeDisabled()
  })

  // NRT https://passculture.atlassian.net/browse/PC-37537
  it('resets correctly when selecting default category and default subcategory after prior selections', async () => {
    let formActions: UseFormReturn<DetailsFormValues>
    renderSubCategories({
      onReady: (actions) => {
        formActions = actions
      },
    })

    const categorySelect = screen.getByLabelText(/Catégorie/)

    await userEvent.selectOptions(categorySelect, 'A')
    await screen.findByLabelText(/Sous-catégorie/)

    // -------------------------------------------------------------------------
    // Case 1: Select default category after having selected a non-default category

    await userEvent.selectOptions(
      categorySelect,
      DEFAULT_DETAILS_FORM_VALUES.categoryId
    )

    expect(screen.queryByLabelText(/Sous-catégorie/)).not.toBeInTheDocument()
    await waitFor(() => {
      expect(formActions.getValues('categoryId')).toBe('')
      expect(formActions.getValues('subcategoryId')).toBe('')
      expect(formActions.getValues('subcategoryConditionalFields')).toEqual([])
    })

    // -------------------------------------------------------------------------
    // Case 2: Select default subcategory after having selected a non-default subcategory

    await userEvent.selectOptions(categorySelect, 'A')
    const subcategorySelect2 = await screen.findByLabelText(/Sous-catégorie/)
    await userEvent.selectOptions(subcategorySelect2, 'sub-A')

    await waitFor(() => {
      expect(formActions.getValues('subcategoryId')).toBe('sub-A')
      expect(formActions.getValues('subcategoryConditionalFields')).toEqual([
        'author',
        'speaker',
        'ean',
      ])
    })

    await userEvent.selectOptions(
      subcategorySelect2,
      DEFAULT_DETAILS_FORM_VALUES.subcategoryId
    )

    await waitFor(() => {
      expect(formActions.getValues('subcategoryId')).toBe('')
      expect(formActions.getValues('subcategoryConditionalFields')).toEqual([])
    })
  })

  it('resets artistic fields when subcategory changes', async () => {
    let formActions!: UseFormReturn<DetailsFormValues>
    renderSubCategories({
      onReady: (actions) => {
        formActions = actions
      },
    })

    const categorySelect = screen.getByLabelText(/Catégorie/)
    await userEvent.selectOptions(categorySelect, 'A')

    const subcategorySelect = await screen.findByLabelText(/Sous-catégorie/)
    await userEvent.selectOptions(subcategorySelect, 'sub-A')

    formActions.setValue('author', 'Test Author')
    formActions.setValue('speaker', 'Test Speaker')
    formActions.setValue('ean', 'Test EAN')

    await waitFor(() => {
      expect(formActions.getValues('author')).toBe('Test Author')
      expect(formActions.getValues('speaker')).toBe('Test Speaker')
      expect(formActions.getValues('ean')).toBe('Test EAN')
    })

    await userEvent.selectOptions(subcategorySelect, 'sub-A2')

    await waitFor(() => {
      expect(formActions.getValues('author')).toBe(
        DEFAULT_DETAILS_FORM_VALUES.author
      )
      expect(formActions.getValues('speaker')).toBe(
        DEFAULT_DETAILS_FORM_VALUES.speaker
      )
      expect(formActions.getValues('ean')).toBe(DEFAULT_DETAILS_FORM_VALUES.ean)
    })
  })
})
