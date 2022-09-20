import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { configureTestStore } from 'store/testUtils'
import { SubmitButton } from 'ui-kit'

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
          <Form>
            <OfferIndividualForm {...props} />
            <SubmitButton isLoading={false}>Submit</SubmitButton>
          </Form>
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
        conditionalFields: [],
        canBeDuo: true,
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
        conditionalFields: [],
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

  it('should render the component', async () => {
    renderOfferIndividualForm({
      initialValues,
      onSubmit,
      props,
    })
    expect(await screen.findByText('Type d’offre')).toBeInTheDocument()
  })

  it('should submit minimal physical offer', async () => {
    renderOfferIndividualForm({
      initialValues,
      onSubmit,
      props,
    })

    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'physical')
    const subCategorySelect = screen.getByLabelText(
      'Choisir une sous-catégorie'
    )
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: true,
          visual: false,
        },
        author: '',
        bookingEmail: '',
        categoryId: 'physical',
        description: '',
        durationMinutes: '',
        externalTicketOfficeUrl: '',
        isDuo: true,
        isEvent: false,
        isNational: false,
        isVenueVirtual: false,
        isbn: '',
        musicSubType: '',
        musicType: '',
        name: 'Le nom de mon offre',
        offererId: 'virtualAndPhysical',
        performer: '',
        receiveNotificationEmails: false,
        showSubType: '',
        showType: '',
        speaker: '',
        stageDirector: '',
        subCategoryFields: ['isDuo'],
        subcategoryId: 'physical',
        url: '',
        venueId: 'physical',
        visa: '',
        withdrawalDelay: undefined,
        withdrawalDetails: '',
        withdrawalType: undefined,
      },
      expect.anything()
    )
  })

  it('should submit minimal virtual offer', async () => {
    renderOfferIndividualForm({
      initialValues,
      onSubmit,
      props,
    })

    const categorySelect = await screen.findByLabelText('Choisir une catégorie')
    await userEvent.selectOptions(categorySelect, 'virtual')
    const subCategorySelect = screen.getByLabelText(
      'Choisir une sous-catégorie'
    )
    await userEvent.selectOptions(subCategorySelect, 'virtual')
    const nameField = screen.getByLabelText("Titre de l'offre")
    await userEvent.type(nameField, 'Le nom de mon offre')
    const urlField = await screen.findByLabelText('URL d’accès à l’offre')

    await userEvent.type(urlField, 'http://example.com/')

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: true,
          visual: false,
        },
        author: '',
        bookingEmail: '',
        categoryId: 'virtual',
        description: '',
        durationMinutes: '',
        externalTicketOfficeUrl: '',
        isDuo: false,
        isEvent: false,
        isNational: false,
        isVenueVirtual: true,
        isbn: '',
        musicSubType: '',
        musicType: '',
        name: 'Le nom de mon offre',
        offererId: 'virtualAndPhysical',
        performer: '',
        receiveNotificationEmails: false,
        showSubType: '',
        showType: '',
        speaker: '',
        stageDirector: '',
        subCategoryFields: [],
        subcategoryId: 'virtual',
        url: 'http://example.com/',
        venueId: 'virtual',
        visa: '',
        withdrawalDelay: undefined,
        withdrawalDetails: '',
        withdrawalType: undefined,
      },
      expect.anything()
    )
  })
})
