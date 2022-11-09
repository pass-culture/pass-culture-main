import React from 'react'

import FormLayout from 'components/FormLayout'
import { InfoBox, TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

const Contact = () => {
  return (
    <>
      <FormLayout.Section
        title="Contact"
        description={
          'Ces informations seront affichées dans votre page lieu, sur l’application pass Culture. ' +
          'Elles permettront aux bénéficiaires de vous contacter en cas de besoin.'
        }
      >
        <FormLayout.Row>
          <PhoneNumberInput name="phoneNumber" isOptional />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            name="email"
            label="Adresse e-mail"
            placeholder="email@exemple.com"
            isOptional
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            name="webSite"
            label="URL de votre site web"
            placeholder="https://exemple.com"
            isOptional
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Notifications de réservations">
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text="Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre."
            />
          }
        >
          <TextInput
            name="bookingEmail"
            label="Adresse e-mail"
            type="email"
            placeholder="email@exemple.com"
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Contact
