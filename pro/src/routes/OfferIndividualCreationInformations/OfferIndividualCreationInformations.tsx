import React, { useEffect, useState } from 'react'

import Spinner from 'components/layout/Spinner'
// TODO (rlecellier): rename into getOfferQueryParams
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { getOfferIndividualVenuesAdapter } from 'core/Venue/adapters'
import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setInitialFormValues,
} from 'new_components/OfferIndividualForm'
import {
  Informations as InformationsScreen,
  IInformationsProps,
} from 'screens/OfferIndividual/Informations'

import { createOfferAdapter } from './adapters'

type TScreenProps = Pick<IInformationsProps, 'offererNames' | 'venueList'>

const OfferIndividualCreationInformations = (): JSX.Element | null => {
  const [isReady, setIsReady] = useState<boolean>(false)
  const [initialValues, setInitialValues] =
    useState<IOfferIndividualFormValues>(FORM_DEFAULT_VALUES)
  const [screenProps, setScreenProps] = useState<TScreenProps>({
    offererNames: [],
    venueList: [],
  })

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const results = await Promise.all([
          getOffererNamesAdapter(),
          getOfferIndividualVenuesAdapter(),
        ])

        if (results.some(res => !res.isOk)) {
          // TODO (rlecellier): handle error with notification at some point
          console.error(results?.find(res => !res.isOk)?.message)
        }

        const [{ payload: offererNames }, { payload: venueList }] = results

        setScreenProps({
          offererNames,
          venueList,
        })

        setInitialValues(values =>
          setInitialFormValues(
            values,
            offererNames,
            offererId,
            venueId,
            venueList
          )
        )
        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return (
    <div>
      {isReady ? (
        <InformationsScreen
          {...screenProps}
          createOfferAdapter={createOfferAdapter}
          initialValues={initialValues}
          isParentReady={isReady}
        />
      ) : (
        <Spinner />
      )}
    </div>
  )
}

export default OfferIndividualCreationInformations
