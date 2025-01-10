import { ListOffersOfferResponseModel } from 'apiClient/v1'
import fullStarIcon from 'icons/full-star.svg'
import { useIndividualOffersContext } from 'pages/IndividualOffers/context/IndividualOffersContext'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './HeadlineOfferCell.module.scss'

type HeadlineOfferCellProps = {
  offer: ListOffersOfferResponseModel
  isRestrictedAsAdmin: boolean
  setIsConfirmDialogOpen: (state: boolean) => void
}

export function HeadlineOfferCell({
  offer,
  setIsConfirmDialogOpen,
}: HeadlineOfferCellProps) {
  const { headlineOfferId, upsertHeadlineOffer, removeHeadlineOffer } =
    useIndividualOffersContext()

  async function onSelect() {
    if (offer.id === headlineOfferId) {
      await removeHeadlineOffer()
    } else {
      if (!headlineOfferId) {
        await upsertHeadlineOffer(offer.id)
      } else {
        setIsConfirmDialogOpen(true)
      }
    }
  }

  return (
    <DropdownItem onSelect={onSelect} asChild>
      <Button variant={ButtonVariant.TERNARY} icon={fullStarIcon}>
        {offer.id === headlineOfferId
          ? 'Ne plus mettre à la une'
          : 'Mettre à la une'}
        <Tag variant={TagVariant.BLUE} className={styles['new-tag']}>
          Nouveau
        </Tag>
      </Button>
    </DropdownItem>
  )
}
