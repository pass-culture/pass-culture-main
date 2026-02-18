import type { ListOffersOfferResponseModel } from '@/apiClient/v1'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import fullBoostedIcon from '@/icons/full-boosted.svg'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

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

  async function onClick() {
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
    <DropdownItem
      onSelect={onClick}
      icon={fullBoostedIcon}
      title={
        offer.id === headlineOffer?.id
          ? 'Ne plus mettre à la une'
          : 'Mettre à la une'
      }
    />
  )
}
