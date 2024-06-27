import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import {
  CategoryResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  categoryFactory,
  getOffererNameFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  IndividualOfferForm,
  IndividualOfferFormProps,
} from '../IndividualOfferForm'
import { IndividualOfferFormValues } from '../types'
import { setDefaultInitialFormValues } from '../utils/setDefaultInitialFormValues'
import { getValidationSchema } from '../validationSchema'

const renderIndividualOfferForm = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: IndividualOfferFormValues
  onSubmit: () => void
  props: IndividualOfferFormProps
}) => {
  return renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={getValidationSchema()}
    >
      <IndividualOfferForm {...props} />
    </Formik>,
    { user: sharedCurrentUserFactory() }
  )
}

describe('IndividualOfferForm', () => {
  let initialValues: IndividualOfferFormValues
  const onSubmit = vi.fn()
  let props: IndividualOfferFormProps
  let categories: CategoryResponseModel[] = []
  let subCategories: SubcategoryResponseModel[] = []
  let offererNames: GetOffererNameResponseModel[]
  let venueList: VenueListItemResponseModel[]

  beforeEach(() => {
    categories = [
      categoryFactory({ id: 'virtual' }),
      categoryFactory({ id: 'physical' }),
    ]
    subCategories = [
      subcategoryFactory({
        id: 'physical',
        categoryId: 'physical',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'virtual',
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
    ]
    offererNames = [
      getOffererNameFactory({
        id: 1,
        name: 'Offerer virtual and physical',
      }),
    ]
    venueList = [
      venueListItemFactory({ isVirtual: true }),
      venueListItemFactory({ isVirtual: false }),
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

  describe('venue banner', () => {
    it('should display venue banner when subcategory is not virtual and venue is only virtual', async () => {
      const onlyVirtualVenueList = [
        venueListItemFactory({
          isVirtual: true,
        }),
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie *')
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie *')
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(screen.getByText('Ajouter un lieu')).toBeInTheDocument()
    })

    it('should not display venue banner when offererId is not set', async () => {
      const onlyVirtualVenueList = [
        venueListItemFactory({
          isVirtual: true,
        }),
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderIndividualOfferForm({
        initialValues: { ...initialValues, offererId: undefined },
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie *')
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie *')
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(screen.queryByText('Ajouter un lieu')).not.toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is virtual', async () => {
      const onlyVirtualVenueList = [
        venueListItemFactory({
          isVirtual: true,
        }),
      ]
      props = { ...props, venueList: onlyVirtualVenueList }

      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie *')
      await userEvent.selectOptions(categorySelect, 'virtual')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie *')
      await userEvent.selectOptions(subcategorySelect, 'virtual')

      expect(screen.queryByText('Ajouter un lieu')).not.toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is not virtual but both venue type exist', async () => {
      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie *')
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie *')
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(screen.queryByText('Ajouter un lieu')).not.toBeInTheDocument()
    })
  })
})
