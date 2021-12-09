import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
// @debt deprecated "Mathilde: should not import utility from legacy page"
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
} from 'core/OfferEducational'
import {
  getCategoriesAdapter,
  getOfferersAdapter,
} from 'core/OfferEducational/adapters'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import { Title } from 'ui-kit'

import { getIsOffererEligibleToEducationalOfferAdapter } from './adapters'
import postOfferAdapter from './adapters/postOfferAdapter'
import style from './OfferEductaionalCreation.module.scss'
import setInitialFormValues from './utils/setInitialFormValues'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalCreation = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const notify = useNotification()

  const createOffer = async (offer: IOfferEducationalFormValues) => {
    const { payload, isOk, message } = await postOfferAdapter(offer)

    if (!isOk) {
      return notify.error(message)
    }

    const queryString = `?structure=${offer.offererId}&lieu=${offer.venueId}`
    history.push(`/offre/${payload.offerId}/scolaire/stocks${queryString}`)
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const results = await Promise.all([
          getCategoriesAdapter(null),
          getOfferersAdapter(offererId),
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
          setInitialFormValues(values, offerers.payload, offererId, venueId)
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return isReady && screenProps ? (
    <>
      <Title className={style.heading} level={1}>
        Créer une nouvelle offre scolaire
      </Title>
      <OfferEducationalScreen
        {...screenProps}
        getIsOffererEligibleToEducationalOfferAdapter={
          getIsOffererEligibleToEducationalOfferAdapter
        }
        initialValues={initialValues}
        mode={Mode.CREATION}
        notify={notify}
        onSubmit={createOffer}
      />
    </>
  ) : (
    <Spinner />
  )
}

export default OfferEducationalCreation
