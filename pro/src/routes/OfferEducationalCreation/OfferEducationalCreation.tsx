import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
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

  const initialValues: OfferEducationalFormValues = {
    category: '',
    subCategory: '',
    title: '',
    description: '',
    duration: 0,
    offererId: '',
    venueId: '',
    offererVenueId: '',
    participants: [],
    accessibility: '',
    phone: '',
    email: '',
    notifications: false,
    notificationEmail: '',
  }

  const { structure, lieu } = queryParamsFromOfferer(location)

  if (structure !== null && structure !== '') {
    initialValues.offererId = structure
  }
  if (lieu !== null && lieu !== '') {
    initialValues.venueId = lieu
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
      onSubmit={(values: OfferEducationalFormValues) => {
        console.log(JSON.stringify(values, null, 2))
      }}
    />
  )
}

export default OfferEducationalCreation
