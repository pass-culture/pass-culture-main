import { useFormikContext } from 'formik'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'

import styles from './FormContactTemplate.module.scss'
import { FormContactTemplateCustomForm } from './FormContactTemplateCustomForm/FormContactTemplateCustomForm'

interface FormContactTemplateProps {
  disableForm: boolean
}

export const FormContactTemplate = ({
  disableForm,
}: FormContactTemplateProps): JSX.Element => {
  const { values, setFieldValue, getFieldMeta } =
    useFormikContext<OfferEducationalFormValues>()

  const contactOptions = [
    {
      label: 'Par email',
      checked: Boolean(values.contactOptions?.email),
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setFieldValue('contactOptions.email', e.target.checked),
      collapsed: (
        <div className={styles['contact-checkbox-inner-control']}>
          <TextInput
            label="Adresse email"
            isOptional
            name="email"
            disabled={disableForm}
            description="Format : email@exemple.com"
          />
        </div>
      ),
    },
    {
      label: 'Par téléphone',
      checked: Boolean(values.contactOptions?.phone),
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setFieldValue('contactOptions.phone', e.target.checked),
      collapsed: (
        <div className={styles['contact-checkbox-inner-control']}>
          <PhoneNumberInput
            name="phone"
            label="Numéro de téléphone"
            disabled={disableForm}
            isOptional
          />
        </div>
      ),
    },
    {
      checked: Boolean(values.contactOptions?.form),
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setFieldValue('contactOptions.form', e.target.checked),
      label: 'Via un formulaire',
      collapsed: <FormContactTemplateCustomForm disableForm={disableForm} />,
    },
  ]

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        name="contactOptions"
        legend={
          <h2 className={styles['subtitle']}>
            Comment les enseignants peuvent-ils vous contacter ? *
          </h2>
        }
        required
        asterisk={false}
        group={contactOptions}
        disabled={disableForm}
        error={getFieldMeta('contactOptions').error}
      />
    </div>
  )
}
