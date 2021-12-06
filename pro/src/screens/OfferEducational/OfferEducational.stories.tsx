import { action } from '@storybook/addon-actions'
import React from 'react'

import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational'

import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

import { categoriesFactory } from './__tests-utils__/categoryFactory'
import { subCategoriesFactory } from './__tests-utils__/subCategoryFactory'
import { userOfferersFactory } from './__tests-utils__/userOfferersFactory'
import OfferEducational from './OfferEducational'

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
  title: 'screens/OfferEducational',
  component: OfferEducational,
  decorators: [withRouterDecorator, withPageTemplate],
}

const mockUserOfferers = userOfferersFactory([{}])

const Template = () => (
  <OfferEducational
    educationalCategories={mockEducationalCategories}
    educationalSubCategories={mockEducationalSubcategories}
    getIsOffererEligibleToEducationalOfferAdapter={() => {
      action('getIsOffererEligibleToEducationalOfferAdapter')
      return Promise.resolve({
        isOk: true,
        message: null,
        payload: { isOffererEligibleToEducationalOffer: true },
      })
    }}
    initialValues={DEFAULT_EAC_FORM_VALUES}
    notify={{
      success: action('success'),
      error: action('error'),
      information: action('information'),
      pending: action('pending'),
    }}
    onSubmit={values => {
      console.log(JSON.stringify(values, null, 2))
    }}
    userOfferers={mockUserOfferers}
  />
)

export const Default = Template.bind({})
