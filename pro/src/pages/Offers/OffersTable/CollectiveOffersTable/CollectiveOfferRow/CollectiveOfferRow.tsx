import classNames from 'classnames'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { Audience } from 'core/shared/types'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'

import { CheckboxCell } from '../../Cells/CheckboxCell'
import { CollectiveActionsCells } from '../../Cells/CollectiveActionsCells'
import { CollectiveOfferStatusCell } from '../../Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { OfferEventDateCell } from '../../Cells/OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from '../../Cells/OfferInstitutionCell'
import { OfferNameCell } from '../../Cells/OfferNameCell/OfferNameCell'
import { OfferVenueCell } from '../../Cells/OfferVenueCell'
import { ThumbCell } from '../../Cells/ThumbCell'
import styles from '../../OfferRow.module.scss'

export type CollectiveOfferRowProps = {
  isSelected: boolean
  offer: CollectiveOfferResponseModel
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  urlSearchFilters: SearchFiltersParams
}

export const CollectiveOfferRow = ({
  offer,
  isSelected,
  selectOffer,
  urlSearchFilters,
}: CollectiveOfferRowProps) => {
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )

  const editionOfferLink = useOfferEditionURL({
    isOfferEducational: true,
    offerId: offer.id,
    isShowcase: Boolean(offer.isShowcase),
  })

  return (
    <tr
      className={classNames(styles['offer-item'], {
        [styles['inactive']]: isOfferDisabled(offer.status),
      })}
      data-testid="offer-item-row"
    >
      <CheckboxCell
        offerName={offer.name}
        isSelected={isSelected}
        disabled={isOfferDisabled(offer.status)}
        selectOffer={() => selectOffer(offer)}
      />

      <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />

      <OfferNameCell
        offer={offer}
        editionOfferLink={editionOfferLink}
        audience={Audience.COLLECTIVE}
      />

      {isCollectiveOffersExpirationEnabled && (
        <OfferEventDateCell offer={offer} />
      )}

      <OfferVenueCell venue={offer.venue} />

      <OfferInstitutionCell
        educationalInstitution={offer.educationalInstitution}
      />

      <CollectiveOfferStatusCell offer={offer} />

      <CollectiveActionsCells
        offer={offer}
        editionOfferLink={editionOfferLink}
        urlSearchFilters={urlSearchFilters}
        isSelected={isSelected}
        deselectOffer={() => selectOffer(offer)}
      />
    </tr>
  )
}
