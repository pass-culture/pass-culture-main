import { useForm } from 'react-hook-form'

import { INDIVIDUAL_OFFER_SUBTYPE } from 'commons/core/Offers/constants'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

export const IndividualOfferType = (): JSX.Element | null => {
  const { register, watch, setValue } = useForm<OfferTypeFormValues>()

  const individualOfferSubtype = watch('individualOfferSubtype')

  return (
    <>
      <FormLayout.Section
        title="Votre offre est :"
        className={styles['subtype-section']}
      >
        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            icon={thingStrokeIcon}
            isChecked={
              individualOfferSubtype === INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
            }
            label="Un bien physique"
            description="Livre, instrument de musique, abonnement, cartes et pass…"
            {...register('individualOfferSubtype')}
            value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}`}
            onChange={() =>
              setValue(
                'individualOfferSubtype',
                INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
              )
            }
          />
        </FormLayout.Row>

        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            icon={strokeVirtualThingIcon}
            isChecked={
              individualOfferSubtype === INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
            }
            label="Un bien numérique"
            description="Ebook, jeu vidéo, abonnement streaming..."
            {...register('individualOfferSubtype')}
            value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}`}
            onChange={() =>
              setValue(
                'individualOfferSubtype',
                INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
              )
            }
          />
        </FormLayout.Row>

        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            icon={strokeDateIcon}
            isChecked={
              individualOfferSubtype === INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
            }
            label="Un évènement physique daté"
            description="Concert, représentation, conférence, ateliers..."
            {...register('individualOfferSubtype')}
            value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}`}
            onChange={() =>
              setValue(
                'individualOfferSubtype',
                INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
              )
            }
          />
        </FormLayout.Row>

        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            icon={strokeVirtualEventIcon}
            isChecked={
              individualOfferSubtype === INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
            }
            label="Un évènement numérique daté"
            description="Livestream, cours en ligne, conférence en ligne..."
            {...register('individualOfferSubtype')}
            value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}`}
            onChange={() =>
              setValue(
                'individualOfferSubtype',
                INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
              )
            }
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
