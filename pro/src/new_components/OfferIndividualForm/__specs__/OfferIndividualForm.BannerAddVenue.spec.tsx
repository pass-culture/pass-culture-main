import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { configureTestStore } from 'store/testUtils'

import {
  IOfferIndividualFormValues,
  validationSchema,
  FORM_DEFAULT_VALUES,
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
  const store = configureTestStore({
    user: { currentUser: { publicName: 'François', isAdmin: false } },
  })
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Formik
          initialValues={initialValues}
          onSubmit={onSubmit}
          validationSchema={validationSchema}
        >
          <OfferIndividualForm {...props} />
        </Formik>
      </MemoryRouter>
    </Provider>
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
    initialValues = { ...FORM_DEFAULT_VALUES }
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
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]
    offererNames = [
      {
        id: 'virtualAndPhysical',
        name: 'Offerer virtual and physical',
      },
    ]
    venueList = [
      {
        id: 'physical',
        name: 'Venue AAAA',
        managingOffererId: 'virtualAndPhysical',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
      {
        id: 'virtual',
        name: 'Venue AAAA',
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
      },
    ]
    props = {
      categories,
      subCategories,
      offererNames,
      venueList,
      readOnlyFields: [],
    }
  })

  describe('venue banner', () => {
    it('should display venue banner when subcategory is not virtual and venue is only virtual', async () => {
      const onlyVirtualVenueList = [
        {
          id: 'virtual',
          name: 'Venue AAAA',
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
        },
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderOfferIndividualForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText(
        'Choisir une catégorie'
      )
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText(
        'Choisir une sous-catégorie'
      )
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(await screen.queryByText('+ Ajouter un lieu')).toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is virtual', async () => {
      const onlyVirtualVenueList = [
        {
          id: 'virtual',
          name: 'Venue AAAA',
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
        },
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderOfferIndividualForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText(
        'Choisir une catégorie'
      )
      await userEvent.selectOptions(categorySelect, 'virtual')
      const subcategorySelect = await screen.findByLabelText(
        'Choisir une sous-catégorie'
      )
      await userEvent.selectOptions(subcategorySelect, 'virtual')

      expect(
        await screen.queryByText('+ Ajouter un lieu')
      ).not.toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is not virtual but both venue type exist', async () => {
      renderOfferIndividualForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText(
        'Choisir une catégorie'
      )
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText(
        'Choisir une sous-catégorie'
      )
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(
        await screen.queryByText('+ Ajouter un lieu')
      ).not.toBeInTheDocument()
    })
  })
})
