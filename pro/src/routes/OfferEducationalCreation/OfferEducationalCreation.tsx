import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import Spinner from 'components/layout/Spinner'
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import {
  INITIAL_EDUCATIONAL_FORM_VALUES,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

import { getCategoriesAdapter, getOfferersAdapter } from './adapters'
import setInitialFormValues from './utils/setInitialFormValues'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalCreation = (): JSX.Element => {
  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(INITIAL_EDUCATIONAL_FORM_VALUES)
  const location = useLocation()
  const { structure, lieu } = queryParamsFromOfferer(location)

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const results = await Promise.all([
          getCategoriesAdapter(null),
          getOfferersAdapter(null),
        ])

        if (results.some(res => !res.isOk)) {
          // handle error with notification at some point
          console.error(results?.find(res => !res.isOk)?.message)
        }

        const [categories, offerers] = results

        setScreenProps({
          educationalCategories: categories.payload.educationalCategories,
          educationalSubCategories: categories.payload.educationalSubCategories,
          userOfferers: offerers.payload,
        })

        setInitialValues(values =>
          setInitialFormValues(values, offerers.payload, structure, lieu)
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, lieu, structure])

  return isReady && screenProps ? (
    <OfferEducationalScreen
      {...screenProps}
      initialValues={initialValues}
      onSubmit={(values: IOfferEducationalFormValues) => {
        console.log(JSON.stringify(values, null, 2))
      }}
    />
  ) : (
    <Spinner />
  )
}

export default OfferEducationalCreation
