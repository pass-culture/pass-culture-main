import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { TextInput } from 'ui-kit'

import { EMAIL_LABEL, PHONE_LABEL } from '../../constants/labels'

const FormContact = (): JSX.Element => (
  <FormLayout.Section
    description={`Ces informations sont affichées sur votre offre.\n Elles permettent aux enseignants et aux chefs d’établissement scolaires de vous contacter.`}
    title="Contact"
  >
    <FormLayout.Row>
      <TextInput label={PHONE_LABEL} name="phone" />
    </FormLayout.Row>
    <FormLayout.Row>
      <TextInput label={EMAIL_LABEL} name="email" />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default FormContact
