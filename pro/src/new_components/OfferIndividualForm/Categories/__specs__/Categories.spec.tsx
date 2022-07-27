import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

import { validationSchema } from '..'
import Categories, { ICategoriesProps } from '../Categories'
import { CATEGORIES_DEFAULT_VALUES } from '../constants'

interface IInitialValues {
  subCategoryFields: string[]
  categoryId: string
  subcategoryId: string
  musicType: string
  musicSubType: string
  showType: string
  showSubType: string
}

const renderCategories = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IInitialValues
  onSubmit: () => void
  props: ICategoriesProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Categories {...props} />
    </Formik>
  )
}

describe('OfferIndividual section: Categories', () => {
  let initialValues: IInitialValues
  const onSubmit = jest.fn()
  let props: ICategoriesProps
  let categories: IOfferCategory[] = []
  let subCategories: IOfferSubCategory[] = []

  beforeEach(() => {
    initialValues = { ...CATEGORIES_DEFAULT_VALUES }
    categories = [
      {
        id: 'A',
        proLabel: 'Catégorie',
        isSelectable: true,
      },
      {
        id: 'B',
        proLabel: 'Catégorie music',
        isSelectable: true,
      },
      {
        id: 'C',
        proLabel: 'Catégorie show',
        isSelectable: true,
      },
    ]
    subCategories = [
      {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'B-A',
        categoryId: 'B',
        proLabel: 'Sous catégorie de B',
        isEvent: false,
        conditionalFields: ['musicType', 'musicSubType'],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'C-A',
        categoryId: 'C',
        proLabel: 'Sous catégorie de C',
        isEvent: false,
        conditionalFields: ['showType', 'showSubType'],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]
    props = { categories, subCategories }
  })

  it('should render the component', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    expect(await screen.findByText('Type d’offre')).toBeInTheDocument()
  })

  it('should display subCategories select when a category is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    expect(
      await screen.findByLabelText('Choisir une sous-catégorie')
    ).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Choisir un type de spectacle')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous type')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un genre musical')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous-genre')
    ).not.toBeInTheDocument()
  })

  it('should not display type select when a standard subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = await screen.findByLabelText(
      'Choisir une sous-catégorie'
    )
    await userEvent.selectOptions(subCategorySelect, 'A-A')

    expect(
      await screen.findByLabelText('Choisir une sous-catégorie')
    ).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Choisir un type de spectacle')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous type')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un genre musical')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous-genre')
    ).not.toBeInTheDocument()
  })

  it('should display musicType selects when a music subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'B')
    const subCategorySelect = screen.getByLabelText(
      'Choisir une sous-catégorie'
    )
    await userEvent.selectOptions(subCategorySelect, 'B-A')

    expect(
      screen.queryByLabelText('Choisir un sous-genre')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un type de spectacle')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous type')
    ).not.toBeInTheDocument()

    const musicSelect = screen.getByLabelText('Choisir un genre musical')
    expect(musicSelect).toBeInTheDocument()

    await userEvent.selectOptions(musicSelect, '520')
    expect(screen.getByLabelText('Choisir un sous-genre')).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Choisir un type de spectacle')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous type')
    ).not.toBeInTheDocument()
  })

  it('should display showType selects when a music subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText(
      'Choisir une sous-catégorie'
    )
    await userEvent.selectOptions(subCategorySelect, 'C-A')

    expect(
      screen.queryByLabelText('Choisir un genre musical')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous-genre')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous type')
    ).not.toBeInTheDocument()

    const showSelect = screen.getByLabelText('Choisir un type de spectacle')
    expect(showSelect).toBeInTheDocument()

    await userEvent.selectOptions(showSelect, '100')
    expect(screen.getByLabelText('Choisir un sous type')).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Choisir un genre musical')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Choisir un sous-genre')
    ).not.toBeInTheDocument()
  })
})
