import React from 'react'

import FormLayout from 'components/FormLayout'
import { InfoBox, TextInput } from 'ui-kit'

export interface IExternalLink {
  readOnlyFields?: string[]
}

const ExternalLink = ({ readOnlyFields }: IExternalLink): JSX.Element => {
  return (
    <FormLayout.Section title="Lien pour le grand public">
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            Ce lien sera affiché au public souhaitant réserver l’offre mais ne
            disposant pas ou plus de crédit sur l’application.
          </InfoBox>
        }
      >
        <TextInput
          label="URL de votre site ou billetterie"
          name="externalTicketOfficeUrl"
          isOptional
          type="text"
          placeholder="https://exemple.com"
          disabled={readOnlyFields?.includes('externalTicketOfficeUrl')}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ExternalLink
