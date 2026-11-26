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
  const isInstitutionEditable = isCollectiveInstitutionEditable(offer)

  const educationalInstitutionsQuery = useSWR(
    isInstitutionEditable ? [GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY] : null,
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
        institutions={
          isInstitutionEditable
            ? educationalInstitutionsQuery.data
            : offer.institution
              ? [offer.institution]
              : []
        }
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
