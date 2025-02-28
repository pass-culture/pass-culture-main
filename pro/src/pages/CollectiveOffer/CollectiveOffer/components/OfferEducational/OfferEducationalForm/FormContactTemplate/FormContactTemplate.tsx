import { useField } from 'formik'
import { useId } from 'react'

import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplate.module.scss'
import { FormContactTemplateCustomForm } from './FormContactTemplateCustomForm/FormContactTemplateCustomForm'

interface FormContactTemplateProps {
  disableForm: boolean
}

export const FormContactTemplate = ({
  disableForm,
}: FormContactTemplateProps): JSX.Element => {
  const [, contactOptionsMeta] = useField({ name: 'contactOptions' })
  const hasError =
    contactOptionsMeta.touched && Boolean(contactOptionsMeta.error)
  const ariaDescribedBy = hasError ? 'error-contactOptions' : undefined

  const formCheckBoxId = useId()

  const contactOptions = [
    {
      name: 'contactOptions.email',
      label: 'Par email',
      ariaDescribedBy,
      childrenOnChecked: (
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
      ),
    },
    {
      name: 'contactOptions.phone',
      label: 'Par téléphone',
      ariaDescribedBy,
      childrenOnChecked: (
        <div className={styles['contact-checkbox-inner-control']}>
          <PhoneNumberInput
            name="phone"
            aria-label="Numéro de téléphone de contact"
            label=""
            disabled={disableForm}
            isOptional
          />
        </div>
      ),
    },
    {
      name: 'contactOptions.form',
      label: 'Via un formulaire',
      id: formCheckBoxId,
      ariaDescribedBy,
      childrenOnChecked: (
        <FormContactTemplateCustomForm
          disableForm={disableForm}
          describedBy={formCheckBoxId}
        />
      ),
    },
  ]

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        groupName="contactOptions"
        legend={
          <h2 className={styles['subtitle']}>
            Comment les enseignants peuvent-ils vous contacter ? *
          </h2>
        }
        hideAsterisk
        group={contactOptions}
        disabled={disableForm}
        variant={CheckboxVariant.BOX}
      />
    </div>
  )
}
