import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'
import { Provider } from 'react-redux'

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
  IOfferIndividualForm,
} from '../OfferIndividualForm'

const renderOfferIndividualForm = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IOfferIndividualFormValues
  onSubmit: () => void
  props: IOfferIndividualForm
}) => {
  const store = configureTestStore({
    user: { currentUser: { publicName: 'François', isAdmin: false } },
  })
  return render(
    <Provider store={store}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
      >
        <OfferIndividualForm {...props} />
      </Formik>
    </Provider>
  )
}

describe('OfferIndividual section: Categories', () => {
  let initialValues: IOfferIndividualFormValues
  const onSubmit = jest.fn()
  let props: IOfferIndividualForm
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
        id: 'B',
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
    props = { categories, subCategories, offererNames, venueList }
  })

  it('should render the component', async () => {
    renderOfferIndividualForm({
      initialValues,
      onSubmit,
      props,
    })
    expect(await screen.findByText('Type d’offre')).toBeInTheDocument()
  })
})
