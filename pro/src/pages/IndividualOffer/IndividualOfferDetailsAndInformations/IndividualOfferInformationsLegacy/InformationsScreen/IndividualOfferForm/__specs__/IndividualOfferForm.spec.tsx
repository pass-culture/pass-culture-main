import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'

import {
  CategoryResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  categoryFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
  getOffererNameFactory,
} from 'commons/utils/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'commons/utils/storeFactories'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { setDefaultInitialFormValues } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferInformationsLegacy/InformationsScreen/IndividualOfferForm/commons/utils/setDefaultInitialFormValues'
import { Button } from 'ui-kit/Button/Button'

import { getValidationSchema } from '../commons/validationSchema'
import {
  IndividualOfferForm,
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
  const contextValues = individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={getValidationSchema}
      >
        <Form>
          <IndividualOfferForm {...props} />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </Form>
      </Formik>
    </IndividualOfferContext.Provider>,
    { user: sharedCurrentUserFactory() }
  )
}

vi.mock('commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

Element.prototype.scrollIntoView = vi.fn()

describe('IndividualOfferForm', () => {
  let initialValues: IndividualOfferFormValues
  const onSubmit = vi.fn()
  let props: IndividualOfferFormProps
  let categories: CategoryResponseModel[] = []
  let subCategories: SubcategoryResponseModel[] = []
  let offererNames: GetOffererNameResponseModel[]
  let venueList: VenueListItemResponseModel[]
  const offererId = 2
  const physicalVenueId = 1
  const virtualVenueId = 2

  beforeEach(() => {
    categories = [
      categoryFactory({ id: 'virtual' }),
      categoryFactory({ id: 'physical' }),
    ]
    subCategories = [
      subcategoryFactory({
        id: 'physical',
        categoryId: 'physical',
        canBeDuo: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'virtual',
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
    ]
    offererNames = [
      getOffererNameFactory({
        id: offererId,
        name: 'Offerer virtual and physical',
      }),
    ]
    venueList = [
      venueListItemFactory({
        id: physicalVenueId,
        isVirtual: false,
      }),
      venueListItemFactory({
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
      isEvent: false,
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

  const imageSectionDataset: (
    | GetIndividualOfferWithAddressResponseModel
    | undefined
  )[] = [getIndividualOfferFactory(), undefined]
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

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'physical')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre *')
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
        isDuo: true,
        isEvent: false,
        isNational: false,
        isVenueVirtual: false,
        ean: '',
        gtl_id: '',
        musicType: '',
        musicSubType: '',
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

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'virtual')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'virtual')
    const nameField = screen.getByLabelText('Titre de l’offre *')
    await userEvent.type(nameField, 'Le nom de mon offre')
    const urlField = await screen.findByLabelText('URL d’accès à l’offre *')

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
        isDuo: false,
        isEvent: false,
        isNational: false,
        isVenueVirtual: true,
        ean: '',
        gtl_id: '',
        musicType: '',
        musicSubType: '',
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
