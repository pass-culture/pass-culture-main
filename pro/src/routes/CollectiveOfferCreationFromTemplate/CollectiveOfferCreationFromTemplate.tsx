import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_FORM_VALUES,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducational from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'domainsOptions' | 'userOfferers' | 'categories'
>

const CollectiveOfferCreationFromTemplate = () => {
  const { templateId } = useParams<{ templateId: string }>()
  const notify = useNotification()

  const [isLoading, setIsLoading] = useState(true)
  const [initialValues, setInitialValues] = useState(DEFAULT_EAC_FORM_VALUES)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)

  useEffect(() => {
    const loadData = async () => {
      const offerTemplateResponse = await getCollectiveOfferTemplateAdapter(
        templateId
      )

      if (!offerTemplateResponse.isOk) {
        return notify.error(offerTemplateResponse.message)
      }

      const result = await getCollectiveOfferFormDataApdater({
        offererId: offerTemplateResponse.payload.venue.managingOffererId,
        offer: offerTemplateResponse.payload,
      })

      if (!result.isOk) {
        notify.error(result.message)
      }

      const { categories, offerers, domains, initialValues } = result.payload

      setScreenProps({
        userOfferers: offerers,
        domainsOptions: domains,
        categories,
      })

      setInitialValues(values =>
        setInitialFormValues(
          {
            ...values,
            ...initialValues,
          },
          offerers,
          offerers[0].id,
          offerTemplateResponse.payload.venueId
        )
      )

      setIsLoading(false)
    }

    loadData()
  }, [])

  if (isLoading || !screenProps) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout
      title="Créer une offre pour un établissement scolaire"
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.DETAILS,
        isCreatingOffer: true,
      }}
    >
      <OfferEducational
        {...screenProps}
        initialValues={initialValues}
        onSubmit={() => {}}
        mode={Mode.CREATION}
      />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferCreationFromTemplate
