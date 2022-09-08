import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { TextInput } from 'ui-kit'

const ExternalLink = (): JSX.Element => {
  return (
    <FormLayout.Section
      title="Lien pour le grand public"
      description="Ce lien sera affiché aux utilisateurs ne pouvant pas effectuer la réservation dans l’application. Nous vous recommandons d’insérer le lien vers votre billetterie ou votre site internet."
    >
      <FormLayout.Row>
        <TextInput
          label="URL de votre site ou billetterie"
          name="externalTicketOfficeUrl"
          isOptional
          type="text"
          placeholder="https://exemple.com"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ExternalLink
