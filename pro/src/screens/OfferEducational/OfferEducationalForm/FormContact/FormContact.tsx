import React from 'react'

import FormLayout from 'components/FormLayout'
import { TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import { EMAIL_LABEL } from '../../constants/labels'
import styles from '../OfferEducationalForm.module.scss'

const FormContact = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => (
  <FormLayout.Section
    description={`Ces informations sont affichées sur votre offre.\n Elles permettent aux enseignants et aux chefs d’établissement scolaires de vous contacter.`}
    title="Contact"
  >
    <FormLayout.Row className={styles['phone-number-row']}>
      <PhoneNumberInput name="phone" disabled={disableForm} />
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

export default FormContact
