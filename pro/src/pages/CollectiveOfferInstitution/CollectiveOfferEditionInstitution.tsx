import { useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  isCollectiveOfferTemplate,
  Mode,
} from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { extractInitialInstitutionValues } from '@/commons/core/OfferEducational/utils/extractInitialInstitutionValues'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isCollectiveInstitutionEditable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferInstitutionScreen } from '@/pages/CollectiveOfferInstitution/components/CollectiveOfferInstitution/CollectiveOfferInstitution'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { getEducationalInstitutions } from './commons/utils/getEducationalInstitutions'

export const CollectiveOfferEditionInstitution = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()

  const educationalInstitutionsQuery = useSWR(
    [GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY],
    () => getEducationalInstitutions(),
    { fallbackData: [] }
  )

  assertOrFrontendError(
    !isCollectiveOfferTemplate(offer),
    '`offer` shoud not be a (collective offer) template.'
  )

  const onSuccess = async ({
    message,
    payload,
  }: {
    message: string
    payload: GetCollectiveOfferResponseModel
  }) => {
    await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      `/offre/${computeURLCollectiveOfferId(
        payload.id,
        false
      )}/collectif/recapitulatif`
    )
    snackBar.success(message)
  }

  if (educationalInstitutionsQuery.isLoading) {
    return <Spinner />
  }

  const isInstitutionEditable = isCollectiveInstitutionEditable(offer)

  return (
    <CollectiveOfferLayout
      offer={offer}
      subTitle={offer.name}
      isTemplate={isTemplate}
    >
      <CollectiveOfferInstitutionScreen
        mode={isInstitutionEditable ? Mode.EDITION : Mode.READ_ONLY}
        initialValues={extractInitialInstitutionValues(
          offer.institution,
          offer.teacher
        )}
        onSuccess={onSuccess}
        institutions={educationalInstitutionsQuery.data}
        isLoadingInstitutions={educationalInstitutionsQuery.isLoading}
        offer={offer}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferEditionInstitution
)
