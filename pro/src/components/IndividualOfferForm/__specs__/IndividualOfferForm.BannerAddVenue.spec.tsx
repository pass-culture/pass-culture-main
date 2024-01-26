import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { OffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import {
  individualOfferCategoryFactory,
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
      validationSchema={getValidationSchema()}
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
  let subCategories: SubcategoryResponseModel[] = []
  let offererNames: OffererName[]
  let venueList: IndividualOfferVenueItem[]

  beforeEach(() => {
    categories = [
      individualOfferCategoryFactory({ id: 'virtual' }),
      individualOfferCategoryFactory({ id: 'physical' }),
    ]
    subCategories = [
      individualOfferSubCategoryFactory({
        id: 'physical',
        categoryId: 'physical',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'virtual',
        categoryId: 'virtual',
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
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

      expect(screen.getByText('+ Ajouter un lieu')).toBeInTheDocument()
    })

    it('should not display venue banner when subcategory is not virtual and offererId is not set but it exist one not virtual venue', async () => {
      offererNames = [
        {
          id: 1,
          name: 'Offerer 1',
        },
        {
          id: 2,
          name: 'Offerer 2',
        },
      ]
      venueList = [
        individualOfferVenueItemFactory({
          isVirtual: true,
          managingOffererId: 1,
        }),
        individualOfferVenueItemFactory({
          isVirtual: false,
          managingOffererId: 1,
        }),
        individualOfferVenueItemFactory({
          isVirtual: true,
          managingOffererId: 2,
        }),
        individualOfferVenueItemFactory({
          isVirtual: false,
          managingOffererId: 2,
        }),
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

    it('should display venue banner when subcategory is not virtual and offererId is not set but it exist only virtual venues', async () => {
      offererNames = [
        {
          id: 1,
          name: 'Offerer 1',
        },
        {
          id: 2,
          name: 'Offerer 2',
        },
      ]
      venueList = [
        individualOfferVenueItemFactory({
          isVirtual: true,
          managingOffererId: 1,
        }),
        individualOfferVenueItemFactory({
          isVirtual: true,
          managingOffererId: 2,
        }),
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

      renderIndividualOfferForm({
        initialValues,
        onSubmit,
        props,
      })

      const categorySelect = await screen.findByLabelText('Catégorie')
      await userEvent.selectOptions(categorySelect, 'physical')
      const subcategorySelect = await screen.findByLabelText('Sous-catégorie')
      await userEvent.selectOptions(subcategorySelect, 'physical')

      expect(screen.getByText('+ Ajouter un lieu')).toBeInTheDocument()
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
