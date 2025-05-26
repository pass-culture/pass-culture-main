import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { useHeadlineOfferContext } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import fullBoostedIcon from 'icons/full-boosted.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'

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
    useHeadlineOfferContext()

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
        <div className={styles['new-tag']}>
          <Tag label="Nouveau" variant={TagVariant.NEW} />
        </div>
      </span>
    </DropdownItem>
  )
}
