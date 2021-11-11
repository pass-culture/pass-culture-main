import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import { categoriesAndSubCategoriesSelector } from 'store/offers/selectors'
import { loadCategories } from 'store/offers/thunks'

import { getEducationalCategories, getEducationalSubCategories } from './utils/getEducationalCategories'

const OfferEducationalCreation = (): JSX.Element => {
  const dispatch = useDispatch()
  const location = useLocation()
  const { categories, subCategories } = useSelector(categoriesAndSubCategoriesSelector)

  const initialValues: Record<string, unknown> = {}
  const queryParams = queryParamsFromOfferer(location)
  
  if (queryParams.structure !== '') {
    initialValues.offererId = queryParams.structure
  }
  if (queryParams.lieu !== '') {
    initialValues.venueId = queryParams.lieu
  }

  const educationalCategories = getEducationalCategories(categories, subCategories)
  const educationalSubcategories = getEducationalSubCategories(subCategories)

  useEffect(() => {
    dispatch(loadCategories())
  }, [dispatch])
  
  return (
    <OfferEducationalScreen
      educationalCategories={educationalCategories}
      educationalSubcategories={educationalSubcategories}
      initialValues={initialValues}
    />
  )
}

export default OfferEducationalCreation
