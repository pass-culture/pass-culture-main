import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { TextInput } from 'ui-kit'

import styles from './contact.module.scss'

const Contact = () => {
  return (
    <FormLayout.Section title="Contact">
      <p className={styles['explanatory-text']}>
        Ces informations seront affichées dans votre page lieu, sur
        l’application pass Culture. Elles permettront aux bénéficiaires de vous
        contacter en cas de besoin.
      </p>
      <FormLayout.Row>
        <TextInput name="phoneNumber" label="Téléphone" />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          name="email"
          label="Adresse e-mail"
          placeholder="email@exemple.com"
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          name="webSite"
          label="URL de votre site web"
          placeholder="https://exemple.com"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default Contact
