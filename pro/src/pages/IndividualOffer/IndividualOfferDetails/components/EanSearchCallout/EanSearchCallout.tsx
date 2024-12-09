import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from './EanSearchCallout.module.scss'

type EanSearchCalloutProps = {
  isDirtyDraftOfferProductBased?: boolean
}

export const EanSearchCallout = ({
  isDirtyDraftOfferProductBased = false,
}: EanSearchCalloutProps) => {
  const calloutVariant = isDirtyDraftOfferProductBased
    ? CalloutVariant.SUCCESS
    : CalloutVariant.INFO
  const calloutLabel = isDirtyDraftOfferProductBased
    ? 'Les informations suivantes ont été synchronisées à partir de l’EAN renseigné.'
    : 'Les informations de cette page ne sont pas modifiables car elles sont liées à l’EAN renseigné.'

  return (
    <Callout className={styles['ean-search-callout']} variant={calloutVariant}>
      {calloutLabel}
    </Callout>
  )
}
