import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './EanSearchCallout.module.scss'

type EanSearchCalloutProps = {
  isDraftOffer: boolean
}

export const EanSearchCallout = ({ isDraftOffer }: EanSearchCalloutProps) => {
  const calloutVariant = isDraftOffer
    ? CalloutVariant.SUCCESS
    : CalloutVariant.INFO
  const calloutLabel = isDraftOffer
    ? 'Les informations suivantes ont été synchronisées à partir de l’EAN renseigné.'
    : 'Les informations de cette page ne sont pas modifiables car elles sont liées à l’EAN renseigné.'

  return (
    <Callout className={styles['ean-search-callout']} variant={calloutVariant}>
      {calloutLabel}
    </Callout>
  )
}
