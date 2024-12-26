import classNames from 'classnames'
import { useField, useFormikContext } from 'formik'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { FieldSetLayout } from 'ui-kit/form/shared/FieldSetLayout/FieldSetLayout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplate.module.scss'
import { FormContactTemplateCustomForm } from './FormContactTemplateCustomForm/FormContactTemplateCustomForm'

interface FormContactTemplateProps {
  disableForm: boolean
}

export const FormContactTemplate = ({
  disableForm,
}: FormContactTemplateProps): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalFormValues>()
  const [, contactOptionsMeta] = useField({ name: 'contactOptions' })
  const hasError =
    contactOptionsMeta.touched && Boolean(contactOptionsMeta.error)
  const ariaDescribedBy = 'error-contactOptions'

  return (
    <FormLayout.Section title="Comment les enseignants peuvent-ils vous contacter ? *">
      <FieldSetLayout
        legend="Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre :"
        name="contactOptions"
        {...(hasError ? { error: contactOptionsMeta.error } : {})}
      >
        <div className={styles['contact-checkbox']}>
          <Checkbox
            label="Par email"
            name="contactOptions.email"
            value=""
            hideFooter
            disabled={disableForm}
            aria-expanded={Boolean(values.contactOptions?.email)}
            {...(hasError ? { ariaDescribedBy } : {})}
          />
          {values.contactOptions?.email && (
            <div className={styles['contact-checkbox-inner-control']}>
              <TextInput
                aria-label="Email de contact"
                label=""
                isOptional
                name="email"
                disabled={disableForm}
                description="Format : email@exemple.com"
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
            {...(hasError ? { ariaDescribedBy } : {})}
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
            {...(hasError ? { ariaDescribedBy } : {})}
          />
          {values.contactOptions?.form && (
            <div className={styles['contact-checkbox-inner-control']}>
              <FormContactTemplateCustomForm disableForm={disableForm} />
            </div>
          )}
        </div>
      </FieldSetLayout>
    </FormLayout.Section>
  )
}
