import { useLocation, useNavigate } from 'react-router-dom'
import useSWR, { useSWRConfig } from 'swr'

import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
} from 'commons/core/OfferEducational/types'
import { extractInitialVisibilityValues } from 'commons/core/OfferEducational/utils/extractInitialVisibilityValues'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferVisibilityScreen } from 'pages/CollectiveOfferVisibility/components/CollectiveOfferVisibility/CollectiveOfferVisibility'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'

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
    <Layout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation={isCreation}
        requestId={requestId}
        offer={offer}
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
      </CollectiveOfferLayout>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferVisibility
)
