import { useLocation } from 'react-router'
import useSWR from 'swr'

import { GET_EDUCATIONAL_INSTITUTIONS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  isCollectiveOfferTemplate,
  Mode,
} from '@/commons/core/OfferEducational/types'
import { extractInitialInstitutionValues } from '@/commons/core/OfferEducational/utils/extractInitialInstitutionValues'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { isCollectiveInstitutionEditable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferInstitutionScreen } from '@/pages/CollectiveOfferInstitution/components/CollectiveOfferInstitution/CollectiveOfferInstitution'

import { getEducationalInstitutions } from './commons/utils/getEducationalInstitutions'

export const CollectiveOfferCreationInstitution = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)
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

  const initialValues = extractInitialInstitutionValues(
    offer.institution,
    offer.teacher
  )

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isTemplate={isTemplate}
      isCreation={isCreation}
      requestId={requestId}
      offer={offer}
    >
      <CollectiveOfferInstitutionScreen
        mode={Mode.CREATION}
        initialValues={initialValues}
        institutions={
          isInstitutionEditable
            ? educationalInstitutionsQuery.data
            : offer.institution
              ? [offer.institution]
              : []
        }
        isLoadingInstitutions={educationalInstitutionsQuery.isLoading}
        offer={offer}
        requestId={requestId}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferCreationInstitution
)
