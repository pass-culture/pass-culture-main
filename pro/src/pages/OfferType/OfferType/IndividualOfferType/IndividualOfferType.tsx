import cn from 'classnames'
import { useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router'

import { INDIVIDUAL_OFFER_SUBTYPE } from 'commons/core/Offers/constants'
import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'

import styles from './IndividualOfferType.module.scss'

export const IndividualOfferType = () => {
  const { setValue, getValues } = useFormContext()
  const location = useLocation()
  const isOnboarding = location.pathname.includes('onboarding')

  return (
    <RadioButtonGroup
      variant="detailed"
      name="individualOfferSubtype"
      className={cn(styles['container'], {
        [styles['container-onboarding']]: isOnboarding,
      })}
      label="Votre offre est"
      labelTag="h2"
      onChange={(e) => setValue('offer.individualOfferSubtype', e.target.value)}
      checkedOption={getValues('offer.individualOfferSubtype')}
      options={[
        {
          label: 'Un bien physique',
          value: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
          description:
            'Livre, instrument de musique, abonnement, cartes et pass…',
          asset: {
            variant: 'icon',
            src: thingStrokeIcon,
          },
        },
        {
          label: 'Un bien numérique',
          value: INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD,
          description: 'Ebook, jeu vidéo, abonnement streaming...',
          asset: {
            variant: 'icon',
            src: strokeVirtualThingIcon,
          },
        },
        {
          label: 'Un évènement physique daté',
          value: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT,
          description: 'Concert, représentation, conférence, ateliers...',
          asset: {
            variant: 'icon',
            src: strokeDateIcon,
          },
        },
        {
          label: 'Un évènement numérique daté',
          value: INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
          description: 'Livestream, cours en ligne, conférence en ligne...',
          asset: {
            variant: 'icon',
            src: strokeVirtualEventIcon,
          },
        },
      ]}
    />
  )
}
