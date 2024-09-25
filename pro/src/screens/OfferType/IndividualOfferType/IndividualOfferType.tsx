import { useFormikContext } from 'formik'
import { useTranslation } from 'react-i18next'

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
  const { t } = useTranslation('common')
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()

  return (
    <>
      <FormLayout.Section
        title={t('your_offer_is')}
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
            label={t('physical_good')}
            description={t('physical_good_description')}
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
            label={t('digital_good')}
            description={t('digital_good_description')}
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
            label={t('physical_event')}
            description={t('physical_event_description')}
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
            label={t('digital_event')}
            description={t('digital_event_description')}
            onChange={handleChange}
            value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}
            dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}`}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
