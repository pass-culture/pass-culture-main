import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setDefaultInitialFormValues,
  validationSchema,
} from '..'
import OfferIndividualForm, {
  IOfferIndividualFormProps,
} from '../OfferIndividualForm'

const renderOfferIndividualForm = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IOfferIndividualFormValues
  onSubmit: () => void
  props: IOfferIndividualFormProps
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
      <OfferIndividualForm {...props} />
    </Formik>,
    { storeOverrides }
  )
}

describe('OfferIndividualForm', () => {
  let initialValues: IOfferIndividualFormValues
  const onSubmit = jest.fn()
  let props: IOfferIndividualFormProps
  let categories: IOfferCategory[] = []
  let subCategories: IOfferSubCategory[] = []
  let offererNames: TOffererName[]
  let venueList: TOfferIndividualVenue[]

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
        nonHumanizedId: 1,
        name: 'Offerer virtual and physical',
      },
    ]
    venueList = [
      {
        nonHumanizedId: 1,
        name: 'Venue AAAA',
        managingOffererId: 'AE',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
      {
        nonHumanizedId: 2,
        name: 'Venue AAAA',
        managingOffererId: 'AE',
        isVirtual: true,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
    ]
    props = {
      categories,
      subCategories,
      offererNames,
      venueList,
      readOnlyFields: [],
      onImageUpload: jest.fn(),
      onImageDelete: jest.fn(),
      offerSubtype: null,
    }
    initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      null,
      null,
      venueList
    )
  })

  describe('venue banner', () => {
    it('should display venue banner when subcategory is not virtual and venue is only virtual', async () => {
      const onlyVirtualVenueList = [
        {
          id: 'virtual',
          name: 'Venue AAAA',
          nonHumanizedId: 3,
          managingOffererId: 'virtualAndPhysical',
          isVirtual: true,
          withdrawalDetails: '',
          accessibility: {
            visual: false,
            mental: false,
            audio: false,
            motor: false,
            none: true,
          },
          hasMissingReimbursementPoint: false,
          hasCreatedOffer: true,
        },
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderOfferIndividualForm({
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
        {
          id: 'virtual',
          name: 'Venue AAAA',
          nonHumanizedId: 4,
          managingOffererId: 'virtualAndPhysical',
          isVirtual: true,
          withdrawalDetails: '',
          accessibility: {
            visual: false,
            mental: false,
            audio: false,
            motor: false,
            none: true,
          },
          hasMissingReimbursementPoint: false,
          hasCreatedOffer: true,
        },
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderOfferIndividualForm({
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
      renderOfferIndividualForm({
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
