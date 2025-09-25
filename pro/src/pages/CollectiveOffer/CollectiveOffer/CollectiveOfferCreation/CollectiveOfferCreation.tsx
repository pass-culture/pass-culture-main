import type { JSX } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { Mode } from '@/commons/core/OfferEducational/types'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import {
  type OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useOfferEducationalFormData'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { OfferEducational } from '../components/OfferEducational/OfferEducational'

export const CollectiveOfferCreation = ({
  offer,
  isTemplate,
}: OptionalCollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const { requete: requestId } = queryParamsFromOfferer(location)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = selectedOffererId?.toString()
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    Number(offererId),
    offer
  )

  return (
    <CollectiveOfferLayout
      subTitle={offer?.name}
      isCreation
      isTemplate={isTemplate}
      requestId={requestId}
      offer={offer}
    >
      {!isReady ? (
        <Spinner />
      ) : (
        <OfferEducational
          userOfferer={offerEducationalFormData.offerer}
          domainsOptions={offerEducationalFormData.domains}
          venues={offerEducationalFormData.venues}
          offer={offer}
          mode={Mode.CREATION}
          isTemplate={isTemplate}
        />
      )}
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOptionalCollectiveOfferFromParams(
  CollectiveOfferCreation
)
