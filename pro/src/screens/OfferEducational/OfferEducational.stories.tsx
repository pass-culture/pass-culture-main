import { DEFAULT_EAC_FORM_VALUES, Mode } from 'core/OfferEducational'
import {
  categoriesFactory,
  managedVenuesFactory,
  subCategoriesFactory,
  userOfferersFactory,
} from './__tests-utils__'

import OfferEducational from './OfferEducational'
import React from 'react'
import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

const mockEducationalCategories = categoriesFactory([
  {
    id: 'MUSEE',
    label: 'Musée, patrimoine, architecture, arts visuels',
  },
  {
    id: 'CINEMA',
    label: 'Cinéma',
  },
])

const mockEducationalSubcategories = subCategoriesFactory([
  {
    id: 'CINE_PLEIN_AIR',
    categoryId: 'CINEMA',
    label: 'Cinéma plein air',
  },
  {
    id: 'EVENEMENT_CINE',
    categoryId: 'CINEMA',
    label: 'Événement cinématographique',
  },
  {
    id: 'VISITE_GUIDEE',
    categoryId: 'MUSEE',
    label: 'Visite guidée',
  },
])

export default {
  title: 'screens/OfferEducationalForm',
  component: OfferEducational,
  decorators: [withRouterDecorator, withPageTemplate],
}

const mockUserOfferers = userOfferersFactory([
  { managedVenues: managedVenuesFactory([{}]) },
])

const Template = () => (
  <OfferEducational
    educationalCategories={mockEducationalCategories}
    educationalSubCategories={mockEducationalSubcategories}
    getIsOffererEligible={() =>
      Promise.resolve({
        isOk: true,
        message: null,
        payload: { isOffererEligibleToEducationalOffer: true },
      })
    }
    initialValues={DEFAULT_EAC_FORM_VALUES}
    mode={Mode.CREATION}
    notify={{
      success: () => null,
      error: () => null,
      information: () => null,
      pending: () => null,
    }}
    onSubmit={values => {
      console.log(JSON.stringify(values, null, 2))
    }}
    userOfferers={mockUserOfferers}
  />
)

export const Default = Template.bind({})
