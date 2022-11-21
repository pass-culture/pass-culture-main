import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOfferTemplate,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import postCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/postCollectiveOfferTemplateAdapter'
import useNotification from 'hooks/useNotification'
// @debt deprecated "Mathilde: should not import utility from legacy page"
import { useCollectiveOfferImageUpload } from 'pages/CollectiveOfferCreation/useCollectiveOfferImageUpload'
import { patchCollectiveOfferTemplateAdapter } from 'pages/CollectiveOfferEdition/adapters/patchCollectiveOfferTemplateAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import Spinner from 'ui-kit/Spinner/Spinner'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'categories' | 'userOfferers' | 'domainsOptions'
>

interface CollectiveOfferTemplateCreationProps {
  offer?: CollectiveOfferTemplate
  setOfferTemplate: (offer: CollectiveOfferTemplate) => void
}

const CollectiveOfferTemplateCreation = ({
  offer,
  setOfferTemplate,
}: CollectiveOfferTemplateCreationProps) => {
  const history = useHistory()
  const location = useLocation()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const notify = useNotification()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, true)

  const createTemplateOffer = async (
    offerValues: IOfferEducationalFormValues
  ) => {
    const adapter =
      offer === undefined
        ? () => postCollectiveOfferTemplateAdapter({ offer: offerValues })
        : () =>
            patchCollectiveOfferTemplateAdapter({
              offer: offerValues,
              initialValues,
              offerId: offer.id,
            })

    const { payload, isOk, message } = await adapter()

    if (!isOk) {
      return notify.error(message)
    }

    await handleImageOnSubmit(offer?.id ?? payload.id)
    if (offer) {
      setOfferTemplate({ ...offer, ...payload })
    }

    history.push(
      `/offre/${payload.id}/collectif/vitrine/creation/recapitulatif`
    )
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const result = await getCollectiveOfferFormDataApdater({
          offererId,
          offer,
        })

        if (!result.isOk) {
          notify.error(result.message)
        }

        const { categories, offerers, domains, initialValues } = result.payload

        setScreenProps({
          categories: categories,
          userOfferers: offerers,
          domainsOptions: domains,
        })

        setInitialValues(values =>
          setInitialFormValues(
            { ...values, ...initialValues },
            offerers,
            offererId,
            venueId
          )
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return isReady && screenProps ? (
    <>
      <OfferEducationalScreen
        {...screenProps}
        getIsOffererEligible={canOffererCreateCollectiveOfferAdapter}
        initialValues={initialValues}
        mode={Mode.CREATION}
        onSubmit={createTemplateOffer}
        isTemplate={true}
        imageOffer={imageOffer}
        onImageDelete={onImageDelete}
        onImageUpload={onImageUpload}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </>
  ) : (
    <Spinner />
  )
}

export default CollectiveOfferTemplateCreation
