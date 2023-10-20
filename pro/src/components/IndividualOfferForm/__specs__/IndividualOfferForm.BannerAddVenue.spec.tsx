import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { CategoryResponseModel } from 'apiClient/v1'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { OffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { individualOfferVenueItemFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualOfferFormValues,
  setDefaultInitialFormValues,
  validationSchema,
} from '..'
import IndividualOfferForm, {
  IndividualOfferFormProps,
} from '../IndividualOfferForm'

const renderIndividualOfferForm = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: IndividualOfferFormValues
  onSubmit: () => void
  props: IndividualOfferFormProps
}) => {
  const storeOverrides = {
    user: { currentUser: { isAdmin: false } },
  }
  return renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      <IndividualOfferForm {...props} />
    </Formik>,
    { storeOverrides }
  )
}

describe('IndividualOfferForm', () => {
  let initialValues: IndividualOfferFormValues
  const onSubmit = vi.fn()
  let props: IndividualOfferFormProps
  let categories: CategoryResponseModel[] = []
  let subCategories: OfferSubCategory[] = []
  let offererNames: OffererName[]
  let venueList: IndividualOfferVenueItem[]

  beforeEach(() => {
    categories = [
      {
        id: 'A',
        proLabel: 'Catégorie',
        isSelectable: true,
      },
      {
        id: 'virtual',
        proLabel: 'Catégorie music',
        isSelectable: true,
      },
      {
        id: 'physical',
        proLabel: 'Catégorie physical',
        isSelectable: true,
      },
    ]
    subCategories = [
      {
        id: 'physical',
        categoryId: 'physical',
        proLabel: 'Sous catégorie de C',
        isEvent: false,
        conditionalFields: ['showType', 'showSubType'],
        canBeDuo: false,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'virtual',
        categoryId: 'virtual',
        proLabel: 'Sous catégorie de C',
        isEvent: false,
        conditionalFields: ['showType', 'showSubType'],
        canBeDuo: false,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]
    offererNames = [
      {
        id: 1,
        name: 'Offerer virtual and physical',
      },
    ]
    venueList = [
      individualOfferVenueItemFactory({ isVirtual: true }),
      individualOfferVenueItemFactory({ isVirtual: false }),
    ]
    props = {
      categories,
      subCategories,
      offererNames,
      venueList,
      readOnlyFields: [],
      onImageUpload: vi.fn(),
      onImageDelete: vi.fn(),
      offerSubtype: null,
    }
    initialValues = setDefaultInitialFormValues(
      offererNames,
      null,
      null,
      venueList,
      true
    )
  })

  describe('venue banner', () => {
    it('should display venue banner when subcategory is not virtual and venue is only virtual', async () => {
      const onlyVirtualVenueList = [
        individualOfferVenueItemFactory({
          isVirtual: true,
        }),
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie')
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie')
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(screen.queryByText('+ Ajouter un lieu')).toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is virtual', async () => {
      const onlyVirtualVenueList = [
        individualOfferVenueItemFactory({
          isVirtual: true,
        }),
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie')
      await userEvent.selectOptions(categorySelect, 'virtual')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie')
      await userEvent.selectOptions(subcategorySelect, 'virtual')

      expect(screen.queryByText('+ Ajouter un lieu')).not.toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is not virtual but both venue type exist', async () => {
      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie')
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie')
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(screen.queryByText('+ Ajouter un lieu')).not.toBeInTheDocument()
    })
  })
})
