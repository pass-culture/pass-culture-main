import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { Mode } from 'commons/core/OfferEducational/types'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { queryParamsFromOfferer } from 'commons/utils/queryParamsFromOfferer'
import {
  OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { useOfferEducationalFormData } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useOfferEducationalFormData'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import { OfferEducational } from '../components/OfferEducational/OfferEducational'

export const CollectiveOfferCreation = ({
  offer,
  isTemplate,
}: OptionalCollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const { requete: requestId } = queryParamsFromOfferer(location)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = selectedOffererId?.toString()
  const { ...offerEducationalFormData } = useOfferEducationalFormData(
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
      <OfferEducational
        userOfferer={offerEducationalFormData.offerer}
        domainsOptions={offerEducationalFormData.domains}
        nationalPrograms={offerEducationalFormData.nationalPrograms}
        offer={offer}
        mode={Mode.CREATION}
        isTemplate={isTemplate}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withOptionalCollectiveOfferFromParams(
  CollectiveOfferCreation
)
