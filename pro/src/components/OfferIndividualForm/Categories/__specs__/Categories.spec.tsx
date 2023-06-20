import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS, INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { SubmitButton } from 'ui-kit'

import Categories, { ICategoriesProps } from '../Categories'
import { CATEGORIES_DEFAULT_VALUES } from '../constants'
import validationSchema from '../validationSchema'

const renderCategories = ({
  initialValues,
  onSubmit,
  props,
}: {
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
  props: ICategoriesProps
}) => {
  render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <Categories {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('OfferIndividual section: Categories', () => {
  let initialValues: Partial<IOfferIndividualFormValues>
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]
    props = {
      categories,
      subCategories,
      offerSubtype: INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
      venueList: [],
    }
  })

  it('should render the component', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    expect(screen.getByLabelText('Catégorie')).toBeInTheDocument()
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
    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'C-A')
    const showSelect = screen.getByLabelText('Type de spectacle')
    await userEvent.selectOptions(showSelect, '100')
    const subShowSelect = screen.getByLabelText('Sous-type')
    await userEvent.selectOptions(subShowSelect, '101')

    await userEvent.click(screen.getByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        author: '',
        categoryId: 'C',
        durationMinutes: '',
        isEvent: false,
        ean: '',
        musicSubType: '',
        musicType: '',
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
    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    expect(screen.getByLabelText('Sous-catégorie')).toBeInTheDocument()

    expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Genre musical')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-genre')).not.toBeInTheDocument()
  })

  it('should not display type select when a standard subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'A-A')

    expect(screen.getByLabelText('Sous-catégorie')).toBeInTheDocument()

    expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Genre musical')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-genre')).not.toBeInTheDocument()
  })

  it('should display musicType selects when a music subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'B')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'B-A')

    expect(screen.queryByLabelText('Sous-genre')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()

    const musicSelect = screen.getByLabelText('Genre musical')
    expect(musicSelect).toBeInTheDocument()

    await userEvent.selectOptions(musicSelect, '520')
    expect(screen.getByLabelText('Sous-genre')).toBeInTheDocument()

    expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()
  })

  it('should display showType selects when a music subCategory is choosed', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'C-A')

    expect(screen.queryByLabelText('Genre musical')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-genre')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()

    const showSelect = screen.getByLabelText('Type de spectacle')
    expect(showSelect).toBeInTheDocument()

    await userEvent.selectOptions(showSelect, '100')
    expect(screen.getByLabelText('Sous-type')).toBeInTheDocument()

    expect(screen.queryByLabelText('Genre musical')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-genre')).not.toBeInTheDocument()
  })

  it('should not display subType selects when a music category is back to default', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props,
    })
    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'C')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'C-A')

    const showSelect = screen.getByLabelText('Type de spectacle')
    expect(showSelect).toBeInTheDocument()

    await userEvent.selectOptions(showSelect, '100')
    expect(screen.getByLabelText('Sous-type')).toBeInTheDocument()

    await userEvent.selectOptions(categorySelect, '')
    expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sous-type')).not.toBeInTheDocument()
  })
})
