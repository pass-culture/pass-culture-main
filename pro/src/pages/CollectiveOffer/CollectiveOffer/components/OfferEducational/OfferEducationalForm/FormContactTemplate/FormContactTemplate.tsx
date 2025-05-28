import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplate.module.scss'
import { FormContactTemplateCustomForm } from './FormContactTemplateCustomForm/FormContactTemplateCustomForm'

interface FormContactTemplateProps {
  disableForm: boolean
}

export const FormContactTemplate = ({
  disableForm,
}: FormContactTemplateProps): JSX.Element => {
  const contactOptions = [
    {
      name: 'contactOptions.email',
      label: 'Par email',
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
      name: 'contactOptions.phone',
      label: 'Par téléphone',
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
      name: 'contactOptions.form',
      label: 'Via un formulaire',
      collapsed: <FormContactTemplateCustomForm disableForm={disableForm} />,
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
      />
    </div>
  )
}
