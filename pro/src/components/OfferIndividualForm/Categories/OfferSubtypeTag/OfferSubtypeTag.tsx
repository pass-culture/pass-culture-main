import cn from 'classnames'
import React from 'react'

import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import { ReactComponent as DateIcon } from 'icons/ico-date.svg'
import { ReactComponent as VirtualEventIcon } from 'icons/ico-virtual-event.svg'
import { ReactComponent as VirtualThingIcon } from 'icons/ico-virtual-thing.svg'
import ThingIcon from 'icons/stroke-thing.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import style from './OfferSubtypeTag.module.scss'

type TagProps = {
  className?: string
  children: React.ReactNode
}

// Style could be refactored with offer status tag and the Tag in ui-kit
// when UIs agree on a common style
const Tag = ({ className, children }: TagProps) => (
  <span className={cn(style['tag'], className)}>{children}</span>
)

type OfferSubtypeTagProps = {
  className?: string
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE
}

export const OfferSubtypeTag = ({
  className,
  offerSubtype,
}: OfferSubtypeTagProps) => {
  switch (offerSubtype) {
    case INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT:
      return (
        <Tag className={className}>
          <DateIcon />
          Évènement physique
        </Tag>
      )
    case INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD:
      return (
        <Tag className={className}>
          <SvgIcon src={ThingIcon} alt="" />
          Bien physique
        </Tag>
      )
    case INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT:
      return (
        <Tag className={className}>
          <VirtualEventIcon />
          Évènement numérique
        </Tag>
      )
    case INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD:
      return (
        <Tag className={className}>
          <VirtualThingIcon />
          Bien numérique
        </Tag>
      )

    default:
      throw Error(`Unknown offer subtype: ${offerSubtype}`)
  }
}
