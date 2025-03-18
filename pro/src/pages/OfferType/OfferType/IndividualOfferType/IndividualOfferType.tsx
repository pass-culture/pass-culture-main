import { useFormContext } from 'react-hook-form'

import { INDIVIDUAL_OFFER_SUBTYPE } from 'commons/core/Offers/constants'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import styles from './IndividualOfferType.module.scss'

export const IndividualOfferType = () => {
  const { setValue, getValues } = useFormContext()

  return (
    <RadioGroup
      name="individualOfferSubtype"
      className={styles['container']}
      legend={<h2 className={styles['legend']}>Votre offre est :</h2>}
      onChange={(e) => setValue('offer.individualOfferSubtype', e.target.value)}
      checkedOption={getValues('offer.individualOfferSubtype')}
      group={[
        {
          label: 'Un bien physique',
          value: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
          description:
            'Livre, instrument de musique, abonnement, cartes et pass…',
          icon: thingStrokeIcon,
        },
        {
          label: 'Un bien numérique',
          value: INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD,
          description: 'Ebook, jeu vidéo, abonnement streaming...',
          icon: strokeVirtualThingIcon,
        },
        {
          label: 'Un évènement physique daté',
          value: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT,
          description: 'Concert, représentation, conférence, ateliers...',
          icon: strokeDateIcon,
        },
        {
          label: 'Un évènement numérique daté',
          value: INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
          description: 'Livestream, cours en ligne, conférence en ligne...',
          icon: strokeVirtualEventIcon,
        },
      ]}
      variant={RadioVariant.BOX}
    />
  )
}
