import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import {
  INITIAL_EDUCATIONAL_FORM_VALUES,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'
import OfferEducationalScreen from 'screens/OfferEducational'
import { categoriesAndSubCategoriesSelector } from 'store/offers/selectors'
import { loadCategories } from 'store/offers/thunks'

import {
  getEducationalCategories,
  getEducationalSubCategories,
} from './utils/getEducationalCategories'

const OfferEducationalCreation = (): JSX.Element => {
  const dispatch = useDispatch()
  const location = useLocation()
  const { categories, subCategories } = useSelector(
    categoriesAndSubCategoriesSelector
  )
  const { structure, lieu } = queryParamsFromOfferer(location)

  const initialValues: IOfferEducationalFormValues = {
    ...INITIAL_EDUCATIONAL_FORM_VALUES,
    offererId: structure
      ? structure
      : INITIAL_EDUCATIONAL_FORM_VALUES.offererId,
    venueId: lieu ? lieu : INITIAL_EDUCATIONAL_FORM_VALUES.venueId,
  }

  const educationalCategories = getEducationalCategories(
    categories,
    subCategories
  )

  const educationalSubcategories = getEducationalSubCategories(subCategories)

  useEffect(() => {
    dispatch(loadCategories())
  }, [dispatch])

  return (
    <OfferEducationalScreen
      educationalCategories={educationalCategories}
      educationalSubcategories={educationalSubcategories}
      initialValues={initialValues}
      onSubmit={(values: IOfferEducationalFormValues) => {
        console.log(JSON.stringify(values, null, 2))
      }}
    />
  )
}

export default OfferEducationalCreation
