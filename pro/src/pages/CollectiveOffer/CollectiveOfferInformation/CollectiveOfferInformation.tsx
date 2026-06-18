import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  GetCollectiveOfferResponseModel,
  PatchCollectiveOfferBodyModel,
} from '@/apiClient/v1'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { PATCH_SUCCESS_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '../CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferInformationForm } from './components/CollectiveOfferInformationForm/CollectiveOfferInformationForm'

export const CollectiveOfferInformation = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()
  const location = useLocation()
  const isEdition = location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)

  const stepUrls = {
    previous: `/offre/${offer.id}/collectif/stocks`,
    next: `/offre/${offer.id}/collectif/etablissement`,
  }
  if (isEdition) {
    stepUrls.previous = getCollectiveOfferLink(offer.id, offer.displayedStatus)
    stepUrls.next = getCollectiveOfferLink(offer.id, offer.displayedStatus)
  }
  if (requestId) {
    stepUrls.previous += `?requete=${requestId}`
    stepUrls.next += `?requete=${requestId}`
  }

  async function saveAndContinue(partialOffer: PatchCollectiveOfferBodyModel) {
    try {
      const response = await api.editCollectiveOffer({
        path: { offer_id: offer.id },
        body: partialOffer,
      })

      await mutate<GetCollectiveOfferResponseModel>(
        [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(offer.id)],
        { ...offer, ...response },
        { revalidate: false }
      )
      navigate(stepUrls.next)
      snackBar.success(PATCH_SUCCESS_MESSAGE)
    } catch (e) {
      if (isErrorAPIError(e) && e.status < 500) {
        throw e
      } else {
        sendSentryCustomError(e)
        snackBar.error(
          "Une erreur est survenue lors de l'enregistrement de votre offre."
        )
      }
    }
  }

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isCreation={!isEdition}
      requestId={requestId}
      offer={offer}
    >
      <CollectiveOfferInformationForm
        offer={offer}
        isCreation={!isEdition}
        saveAndContinue={saveAndContinue}
        goBackLink={stepUrls.previous}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferInformation
)
