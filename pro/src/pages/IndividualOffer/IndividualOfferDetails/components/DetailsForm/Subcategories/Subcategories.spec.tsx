import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import {
  categoryFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'

import { Subcategories } from './Subcategories'

const categories = [
  categoryFactory({ id: 'A', proLabel: 'Catégorie A', isSelectable: true }),
]

const subcategories = [
  subcategoryFactory({
    id: 'sub-A',
    categoryId: 'A',
    proLabel: 'Sous-catégorie A1',
    conditionalFields: ['ean'],
  }),
  subcategoryFactory({
    id: 'sub-B',
    categoryId: 'B',
    proLabel: 'Sous-catégorie B1',
  }),
]

const SubcategoriesForm = ({
  readOnlyFields = [],
}: {
  readOnlyFields?: string[]
}) => {
  const methods = useForm<DetailsFormValues>({
    defaultValues: {
      ...DEFAULT_DETAILS_FORM_VALUES,
    },
  })

  return (
    <FormProvider {...methods}>
      <Subcategories
        readOnlyFields={readOnlyFields}
        filteredCategories={categories}
        filteredSubcategories={subcategories}
      />
    </FormProvider>
  )
}

const renderSubCategories = (options?: { readOnlyFields?: string[] }) => {
  return render(<SubcategoriesForm {...options} />)
}

describe('<Subcategories />', () => {
  it('renders the category select', () => {
    renderSubCategories()
    expect(screen.getByLabelText('Catégorie *')).toBeInTheDocument()
  })

  it('renders subcategory select only after selecting a category', async () => {
    renderSubCategories()

    expect(screen.queryByLabelText('Sous-catégorie *')).not.toBeInTheDocument()

    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')

    expect(await screen.findByLabelText('Sous-catégorie *')).toBeInTheDocument()
  })

  it('disables selects when readOnlyFields is set', () => {
    renderSubCategories({ readOnlyFields: ['categoryId', 'subcategoryId'] })
    expect(screen.getByLabelText('Catégorie *')).toBeDisabled()
  })
})
