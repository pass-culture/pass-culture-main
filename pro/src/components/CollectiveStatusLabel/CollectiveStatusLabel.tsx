import { CollectiveOfferDisplayedStatus } from '@/apiClient//v1'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'

const COLLECTIVE_OFFER_STATUS_PROPERTIES: Record<
  string,
  {
    variant: TagVariant
    label: string
  }
> = {
  [CollectiveOfferDisplayedStatus.PUBLISHED]: {
    variant: TagVariant.SUCCESS,
    label: 'publiée',
  },
  [CollectiveOfferDisplayedStatus.UNDER_REVIEW]: {
    variant: TagVariant.DEFAULT,
    label: 'en instruction',
  },
  [CollectiveOfferDisplayedStatus.REJECTED]: {
    variant: TagVariant.ERROR,
    label: 'non conforme',
  },
  [CollectiveOfferDisplayedStatus.PREBOOKED]: {
    variant: TagVariant.WARNING,
    label: 'préréservée',
  },
  [CollectiveOfferDisplayedStatus.BOOKED]: {
    variant: TagVariant.SUCCESS,
    label: 'réservée',
  },
  [CollectiveOfferDisplayedStatus.HIDDEN]: {
    variant: TagVariant.DEFAULT,
    label: 'en pause',
  },
  [CollectiveOfferDisplayedStatus.EXPIRED]: {
    variant: TagVariant.ERROR,
    label: 'expirée',
  },
  [CollectiveOfferDisplayedStatus.ENDED]: {
    variant: TagVariant.SUCCESS,
    label: 'terminée',
  },
  [CollectiveOfferDisplayedStatus.CANCELLED]: {
    variant: TagVariant.ERROR,
    label: 'annulée',
  },
  [CollectiveOfferDisplayedStatus.REIMBURSED]: {
    variant: TagVariant.SUCCESS,
    label: 'remboursée',
  },
  [CollectiveOfferDisplayedStatus.ARCHIVED]: {
    variant: TagVariant.DEFAULT,
    label: 'archivée',
  },
  [CollectiveOfferDisplayedStatus.DRAFT]: {
    variant: TagVariant.DEFAULT,
    label: 'brouillon',
  },
}

type CollectiveStatusLabelProps = {
  offerDisplayedStatus: CollectiveOfferDisplayedStatus
}

export const CollectiveStatusLabel = ({
  offerDisplayedStatus,
}: CollectiveStatusLabelProps) => {
  return (
    <Tag
      label={COLLECTIVE_OFFER_STATUS_PROPERTIES[offerDisplayedStatus].label}
      variant={COLLECTIVE_OFFER_STATUS_PROPERTIES[offerDisplayedStatus].variant}
    />
  )
}
