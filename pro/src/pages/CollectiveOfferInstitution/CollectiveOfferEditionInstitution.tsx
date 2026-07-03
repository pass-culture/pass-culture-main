import useSWR from 'swr'

import { GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  isCollectiveOfferTemplate,
  Mode,
} from '@/commons/core/OfferEducational/types'
import { extractInitialInstitutionValues } from '@/commons/core/OfferEducational/utils/extractInitialInstitutionValues'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
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
  const educationalInstitutionsQuery = useSWR(
    [GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY],
    () => getEducationalInstitutions(),
    { fallbackData: [] }
  )

  assertOrFrontendError(
    !isCollectiveOfferTemplate(offer),
    '`offer` shoud not be a (collective offer) template.'
  )

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
