
import { OfferStatus } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDraftIcon from 'icons/stroke-draft.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

const OFFER_STATUS_PROPERTIES: Record<
  string,
  {
    variant: TagVariant
    icon: string
    label: string
  }
> = {
  [OfferStatus.EXPIRED]: {
    variant: TagVariant.DARK_GREY,
    icon: strokeCalendarIcon,
    label: 'expirée',
  },
  [OfferStatus.SOLD_OUT]: {
    variant: TagVariant.RED,
    icon: strokeWarningIcon,
    label: 'épuisée',
  },
  [OfferStatus.ACTIVE]: {
    variant: TagVariant.GREEN,
    icon: strokeCheckIcon,
    label: 'publiée',
  },
  [OfferStatus.DRAFT]: {
    variant: TagVariant.PURPLE,
    icon: strokeDraftIcon,
    label: 'brouillon',
  },
  [OfferStatus.REJECTED]: {
    variant: TagVariant.BLACK,
    icon: strokeCloseIcon,
    label: 'refusée',
  },
  [OfferStatus.PENDING]: {
    variant: TagVariant.DARK_GREY,
    icon: strokeClockIcon,
    label: 'en attente',
  },
  [OfferStatus.INACTIVE]: {
    variant: TagVariant.DARK_GREY,
    icon: fullHideIcon,
    label: 'désactivée',
  },
}

const NEW_OFFER_STATUS_PROPERTIES: Record<
  string,
  {
    variant: TagVariant
    icon: string
    label: string
  }
> = {
  ...OFFER_STATUS_PROPERTIES,
  [OfferStatus.REJECTED]: {
    ...OFFER_STATUS_PROPERTIES[OfferStatus.REJECTED],
    label: 'non conforme',
  },
  [OfferStatus.PENDING]: {
    ...OFFER_STATUS_PROPERTIES[OfferStatus.PENDING],
    label: 'en instruction',
  },
  [OfferStatus.INACTIVE]: {
    ...OFFER_STATUS_PROPERTIES[OfferStatus.PENDING],
    label: 'en pause',
  },
}

type StatusLabelProps = {
  status: OfferStatus
}

export const StatusLabel = ({ status }: StatusLabelProps) => {
  const areNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
  const statusProperties = areNewStatusesEnabled
    ? NEW_OFFER_STATUS_PROPERTIES
    : OFFER_STATUS_PROPERTIES

  return (
    <Tag variant={statusProperties[status].variant}>
      <SvgIcon alt="" src={statusProperties[status].icon} />
      {statusProperties[status].label}
    </Tag>
  )
}
