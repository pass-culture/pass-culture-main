import classNames from 'classnames'
import { useField, useFormikContext } from 'formik'

import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import { Checkbox, TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'
import { FieldSetLayout } from 'ui-kit/form/shared'

import styles from './FormContactTemplate.module.scss'
import FormContactCustomForm from './FormContactTemplateCustomForm/FormContactTemplateCustomForm'

export default function FormContactTemplate({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element {
  const { values } = useFormikContext<OfferEducationalFormValues>()

  const [, contactOptionsMeta] = useField({ name: 'contactOptions' })

  return (
    <FormLayout.Section title="Contact">
      <FieldSetLayout
        legend="Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre :"
        name="contactOptions"
        error={
          contactOptionsMeta.touched && Boolean(contactOptionsMeta.error)
            ? contactOptionsMeta.error
            : undefined
        }
      >
        <div className={styles['contact-checkbox']}>
          <Checkbox
            label="Par email"
            name="contactOptions.email"
            value=""
            hideFooter
            disabled={disableForm}
            aria-expanded={Boolean(values.contactOptions?.email)}
          />
          {values.contactOptions?.email && (
            <div className={styles['contact-checkbox-inner-control']}>
              <TextInput
                aria-label="Email de contact"
                label=""
                isOptional
                name="email"
                disabled={disableForm}
                placeholder="email@exemple.com"
              />
            </div>
          )}
        </div>
        <div
          className={classNames(
            styles['contact-checkbox'],
            styles['phone-number-row']
          )}
        >
          <Checkbox
            label="Par téléphone"
            name="contactOptions.phone"
            value=""
            hideFooter
            disabled={disableForm}
            aria-expanded={Boolean(values.contactOptions?.phone)}
          />
          {values.contactOptions?.phone && (
            <div className={styles['contact-checkbox-inner-control']}>
              <PhoneNumberInput
                name="phone"
                aria-label="Numéro de téléphone de contact"
                label=""
                disabled={disableForm}
                isOptional
              />
            </div>
          )}
        </div>
        <div className={styles['contact-checkbox']}>
          <Checkbox
            label={
              <span>
                <i>Via</i> un formulaire
              </span>
            }
            name="contactOptions.form"
            value=""
            hideFooter
            disabled={disableForm}
            aria-expanded={Boolean(values.contactOptions?.form)}
          />
          {values.contactOptions?.form && (
            <div className={styles['contact-checkbox-inner-control']}>
              <FormContactCustomForm disableForm={disableForm} />
            </div>
          )}
        </div>
      </FieldSetLayout>
    </FormLayout.Section>
  )
}
