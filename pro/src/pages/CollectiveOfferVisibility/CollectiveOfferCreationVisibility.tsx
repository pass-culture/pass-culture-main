import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import useSWR, { useSWRConfig } from 'swr'

import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  isCollectiveOfferTemplate,
  isCollectiveOffer,
  Mode,
} from 'core/OfferEducational/types'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import { CollectiveOfferVisibilityScreen } from 'screens/CollectiveOfferVisibility/CollectiveOfferVisibility'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

import { getEducationalInstitutions } from './getEducationalInstitutions'

export const CollectiveOfferVisibility = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)
  const { mutate } = useSWRConfig()

  const educationalInstitutionsQuery = useSWR(
    [GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY],
    () => getEducationalInstitutions(),
    { fallbackData: [] }
  )

  const onSuccess = async ({
    offerId,
    payload,
  }: {
    offerId: string
    payload: GetCollectiveOfferResponseModel
  }) => {
    await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY], payload, {
      revalidate: false,
    })

    navigate(`/offre/${offerId}/collectif/creation/recapitulatif`)
  }

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error(
      'Impossible de mettre à jour la visibilité d’une offre vitrine.'
    )
  }

  const initialValues = extractInitialVisibilityValues(offer.institution)

  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation={isCreation}
        requestId={requestId}
      >
        <CollectiveOfferVisibilityScreen
          mode={Mode.CREATION}
          initialValues={initialValues}
          onSuccess={onSuccess}
          institutions={educationalInstitutionsQuery.data}
          isLoadingInstitutions={educationalInstitutionsQuery.isLoading}
          offer={offer}
          requestId={requestId}
        />
        <RouteLeavingGuardCollectiveOfferCreation />
      </CollectiveOfferLayout>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferVisibility
)
