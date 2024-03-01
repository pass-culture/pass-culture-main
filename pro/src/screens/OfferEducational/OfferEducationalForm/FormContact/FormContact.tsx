import FormLayout from 'components/FormLayout'
import { TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import { EMAIL_LABEL } from '../../constants/labels'

import styles from './FormContact.module.scss'

export default function FormContact({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element {
  return (
    <FormLayout.Section
      description={`Ces informations sont affichées sur votre offre.\n Elles permettent aux enseignants et aux chefs d’établissement de vous contacter.`}
      title="Contact"
    >
      <FormLayout.Row className={styles['phone-number-row']}>
        <PhoneNumberInput
          name="phone"
          label="Téléphone"
          disabled={disableForm}
          isOptional
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          label={EMAIL_LABEL}
          name="email"
          disabled={disableForm}
          placeholder="email@exemple.com"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
