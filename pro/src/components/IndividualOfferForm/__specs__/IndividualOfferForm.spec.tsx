import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { OffererName } from 'core/Offerers/types'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { SubmitButton } from 'ui-kit'
import {
  individualOfferCategoryFactory,
  individualOfferContextFactory,
  individualOfferFactory,
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualOfferFormValues,
  setDefaultInitialFormValues,
  getValidationSchema,
} from '..'
import IndividualOfferForm, {
  IndividualOfferFormProps,
} from '../IndividualOfferForm'

const renderIndividualOfferForm = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
  contextOverride = {},
}: {
  initialValues: IndividualOfferFormValues
  onSubmit: () => void
  props: IndividualOfferFormProps
  contextOverride?: Partial<IndividualOfferContextValues>
}) => {
  const storeOverrides = {
    user: { currentUser: { isAdmin: false } },
  }
  const contextValues = individualOfferContextFactory(contextOverride)

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={getValidationSchema}
      >
        <Form>
          <IndividualOfferForm {...props} />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </Form>
      </Formik>
    </IndividualOfferContext.Provider>,
    { storeOverrides }
  )
}

describe('IndividualOfferForm', () => {
  let initialValues: IndividualOfferFormValues
  const onSubmit = vi.fn()
  let props: IndividualOfferFormProps
  let categories: CategoryResponseModel[] = []
  let subCategories: SubcategoryResponseModel[] = []
  let offererNames: OffererName[]
  let venueList: IndividualOfferVenueItem[]
  const offererId = 2
  const physicalVenueId = 1
  const virtualVenueId = 2

  beforeEach(() => {
    categories = [
      individualOfferCategoryFactory({ id: 'virtual' }),
      individualOfferCategoryFactory({ id: 'physical' }),
    ]
    subCategories = [
      individualOfferSubCategoryFactory({
        id: 'physical',
        categoryId: 'physical',
        canBeDuo: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'virtual',
        categoryId: 'virtual',
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
    ]
    offererNames = [
      {
        id: offererId,
        name: 'Offerer virtual and physical',
      },
    ]
    venueList = [
      individualOfferVenueItemFactory({
        id: physicalVenueId,
        isVirtual: false,
      }),
      individualOfferVenueItemFactory({
        id: virtualVenueId,
        isVirtual: true,
      }),
    ]
    props = {
      categories,
      subCategories,
      offererNames,
      venueList,
      onImageUpload: vi.fn(),
      onImageDelete: vi.fn(),
      offerSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
    }
    initialValues = setDefaultInitialFormValues(
      offererNames,
      null,
      null,
      venueList,
      true
    )
  })

  it('should render the component', async () => {
    renderIndividualOfferForm({
      initialValues,
      onSubmit,
      props,
    })
    expect(await screen.findByText('Type d’offre')).toBeInTheDocument()
  })

  const imageSectionDataset: (IndividualOffer | undefined)[] = [
    individualOfferFactory(),
    undefined,
  ]
  it.each(imageSectionDataset)(
    'should render image section when offer is given',
    async (offer) => {
      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
        contextOverride: { offer },
      })
      expect(await screen.findByText('Type d’offre')).toBeInTheDocument()
    }
  )

  it('should submit minimal physical offer', async () => {
    initialValues = setDefaultInitialFormValues(
      offererNames,
      null,
      physicalVenueId.toString(),
      venueList,
      true
    )
    renderIndividualOfferForm({
      initialValues,
      onSubmit,
      props,
    })

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'physical')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        accessibility: {
          audio: true,
          mental: true,
          motor: true,
          none: false,
          visual: true,
        },
        author: '',
        bookingEmail: '',
        bookingContact: '',
        categoryId: 'physical',
        description: '',
        durationMinutes: '',
        externalTicketOfficeUrl: '',
        isDuo: true,
        isEvent: false,
        isNational: false,
        isVenueVirtual: false,
        ean: '',
        musicSubType: '',
        musicType: '',
        name: 'Le nom de mon offre',
        offererId: offererId.toString(),
        performer: '',
        receiveNotificationEmails: false,
        showSubType: '',
        showType: '',
        speaker: '',
        stageDirector: '',
        subCategoryFields: ['isDuo'],
        subcategoryId: 'physical',
        url: '',
        venueId: physicalVenueId.toString(),
        visa: '',
        withdrawalDelay: undefined,
        withdrawalDetails: '',
        withdrawalType: undefined,
      },
      expect.anything()
    )
  })

  it('should submit minimal virtual offer', async () => {
    initialValues = setDefaultInitialFormValues(
      offererNames,
      null,
      virtualVenueId.toString(),
      venueList,
      true
    )
    renderIndividualOfferForm({
      initialValues,
      onSubmit,
      props,
    })

    const categorySelect = await screen.findByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'virtual')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'virtual')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')
    const urlField = await screen.findByLabelText('URL d’accès à l’offre')

    await userEvent.type(urlField, 'https://example.com/')

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        accessibility: {
          audio: true,
          mental: true,
          motor: true,
          none: false,
          visual: true,
        },
        author: '',
        bookingEmail: '',
        bookingContact: '',
        categoryId: 'virtual',
        description: '',
        durationMinutes: '',
        externalTicketOfficeUrl: '',
        isDuo: false,
        isEvent: false,
        isNational: false,
        isVenueVirtual: true,
        ean: '',
        musicSubType: '',
        musicType: '',
        name: 'Le nom de mon offre',
        offererId: offererId.toString(),
        performer: '',
        receiveNotificationEmails: false,
        showSubType: '',
        showType: '',
        speaker: '',
        stageDirector: '',
        subCategoryFields: [],
        subcategoryId: 'virtual',
        url: 'https://example.com/',
        venueId: virtualVenueId.toString(),
        visa: '',
        withdrawalDelay: undefined,
        withdrawalDetails: '',
        withdrawalType: undefined,
      },
      expect.anything()
    )
  })
})
