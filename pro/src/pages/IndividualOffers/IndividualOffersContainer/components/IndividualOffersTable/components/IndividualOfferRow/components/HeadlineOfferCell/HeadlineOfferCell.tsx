import { ListOffersOfferResponseModel } from 'apiClient/v1'
import fullBoostedIcon from 'icons/full-boosted.svg'
import { useIndividualOffersContext } from 'pages/IndividualOffers/context/IndividualOffersContext'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './HeadlineOfferCell.module.scss'

type HeadlineOfferCellProps = {
  offer: ListOffersOfferResponseModel
  setIsConfirmReplacementDialogOpen: (state: boolean) => void
  setIsOfferWithoutImageDialogOpen: (state: boolean) => void
}

export function HeadlineOfferCell({
  offer,
  setIsConfirmReplacementDialogOpen,
  setIsOfferWithoutImageDialogOpen,
}: HeadlineOfferCellProps) {
  const { headlineOffer, upsertHeadlineOffer, removeHeadlineOffer } =
    useIndividualOffersContext()

  async function onSelect() {
    if (offer.id === headlineOffer?.id) {
      await removeHeadlineOffer()
    } else {
      if (!offer.thumbUrl) {
        setIsOfferWithoutImageDialogOpen(true)
      } else {
        if (!headlineOffer?.id) {
          await upsertHeadlineOffer({
            offerId: offer.id,
            context: { actionType: 'add' },
          })
        } else {
          setIsConfirmReplacementDialogOpen(true)
        }
      }
    }
  }

  return (
    <DropdownItem onSelect={onSelect} asChild>
      <span>
        <Button variant={ButtonVariant.TERNARY} icon={fullBoostedIcon}>
          {offer.id === headlineOffer?.id
            ? 'Ne plus mettre à la une'
            : 'Mettre à la une'}
        </Button>
        <Tag variant={TagVariant.BLUE} className={styles['new-tag']}>
          Nouveau
        </Tag>
      </span>
    </DropdownItem>
  )
}
