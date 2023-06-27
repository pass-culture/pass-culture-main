import cn from 'classnames'
import React from 'react'

import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import DateIcon from 'icons/ico-date.svg'
import ThingIcon from 'icons/ico-thing.svg'
import VirtualEventIcon from 'icons/ico-virtual-event.svg'
import VirtualThingIcon from 'icons/ico-virtual-thing.svg'

import style from './OfferSubtypeTag.module.scss'

type ITagProps = {
  className?: string
  children: React.ReactNode
}

// Style could be refactored with offer status tag and the Tag in ui-kit
// when UIs agree on a common style
export const Tag = ({ className, children }: ITagProps) => (
  <span className={cn(style['tag'], className)}>{children}</span>
)

type IOfferSubtypeTagProps = {
  className?: string
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE
}

export const OfferSubtypeTag = ({
  className,
  offerSubtype,
}: IOfferSubtypeTagProps) => {
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
          <ThingIcon />
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
