import { useFormikContext } from 'formik'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

export const IndividualOfferType = (): JSX.Element | null => {
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()

  return (
    <>
      <FormLayout.Section
        title="Votre offre est :"
        className={styles['subtype-section']}
      >
        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            name="individualOfferSubtype"
            icon={thingStrokeIcon}
            isChecked={
              values.individualOfferSubtype ===
              INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
            }
            label="Un bien physique"
            description="Livre, instrument de musique, abonnement, cartes et pass…"
            onChange={handleChange}
            value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}`}
          />
        </FormLayout.Row>

        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            name="individualOfferSubtype"
            icon={strokeVirtualThingIcon}
            isChecked={
              values.individualOfferSubtype ===
              INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
            }
            label="Un bien numérique"
            description="Ebook, jeu vidéo, abonnement streaming..."
            onChange={handleChange}
            value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}`}
          />
        </FormLayout.Row>

        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            name="individualOfferSubtype"
            icon={strokeDateIcon}
            isChecked={
              values.individualOfferSubtype ===
              INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
            }
            label="Un évènement physique daté"
            description="Concert, représentation, conférence, ateliers..."
            onChange={handleChange}
            value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}`}
          />
        </FormLayout.Row>

        <FormLayout.Row inline mdSpaceAfter>
          <RadioButtonWithImage
            className={styles['individual-radio-button']}
            name="individualOfferSubtype"
            icon={strokeVirtualEventIcon}
            isChecked={
              values.individualOfferSubtype ===
              INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
            }
            label="Un évènement numérique daté"
            description="Livestream, cours en ligne, conférence en ligne..."
            onChange={handleChange}
            value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}`}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
