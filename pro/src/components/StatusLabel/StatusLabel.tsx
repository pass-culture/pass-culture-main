import { OfferStatus } from 'apiClient/v1'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDraftIcon from 'icons/stroke-draft.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'

const OFFER_STATUS_PROPERTIES: Record<
  string,
  {
    variant: TagVariant
    icon: string
    label: string
  }
> = {
  [OfferStatus.EXPIRED]: {
    variant: TagVariant.ERROR,
    icon: strokeCalendarIcon,
    label: 'expirée',
  },
  [OfferStatus.SOLD_OUT]: {
    variant: TagVariant.ERROR,
    icon: strokeWarningIcon,
    label: 'épuisée',
  },
  [OfferStatus.ACTIVE]: {
    variant: TagVariant.SUCCESS,
    icon: strokeCheckIcon,
    label: 'publiée',
  },
  [OfferStatus.DRAFT]: {
    variant: TagVariant.DEFAULT,
    icon: strokeDraftIcon,
    label: 'brouillon',
  },
  [OfferStatus.REJECTED]: {
    variant: TagVariant.ERROR,
    icon: strokeCloseIcon,
    label: 'non conforme',
  },
  [OfferStatus.PENDING]: {
    variant: TagVariant.DEFAULT,
    icon: strokeClockIcon,
    label: 'en instruction',
  },
  [OfferStatus.INACTIVE]: {
    variant: TagVariant.DEFAULT,
    icon: fullHideIcon,
    label: 'en pause',
  },
}

type StatusLabelProps = {
  status: OfferStatus
}

export const StatusLabel = ({ status }: StatusLabelProps) => {
  return (
    <Tag
      label={OFFER_STATUS_PROPERTIES[status].label}
      variant={OFFER_STATUS_PROPERTIES[status].variant}
    />
  )
}
