import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { OffererName } from 'core/Offerers/types'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import {
  OfferCategory,
  IndividualOffer,
  OfferSubCategory,
} from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { SubmitButton } from 'ui-kit'
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
  const contextValues: IndividualOfferContextValues = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    setSubcategory: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
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
  let categories: OfferCategory[] = []
  let subCategories: OfferSubCategory[] = []
  let offererNames: OffererName[]
  let venueList: IndividualOfferVenueItem[]
  const offererId = 2
  const physicalVenueId = 1
  const virtualVenueId = 2

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
        conditionalFields: [],
        canBeDuo: true,
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
        conditionalFields: [],
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

  const imageSectionDataset: (Partial<IndividualOffer> | undefined)[] = [
    {
      stocks: [],
    },
    undefined,
  ]
  it.each(imageSectionDataset)(
    'should render image section when offer is given',
    async offer => {
      const contextOverride: Partial<IndividualOfferContextValues> = {
        offer: offer ? (offer as IndividualOffer) : undefined,
      }

      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
        contextOverride,
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
