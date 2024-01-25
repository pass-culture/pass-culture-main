import React from 'react'

import Callout from 'components/Callout/Callout'
import FormLayout from 'components/FormLayout'
import { TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

export interface ContactProps {
  isVenueVirtual?: boolean
  isCreatingVenue?: boolean
}
const Contact = ({ isVenueVirtual = false, isCreatingVenue }: ContactProps) => {
  return (
    <>
      {!isCreatingVenue && !isVenueVirtual && (
        <FormLayout.Section
          title="Contact"
          description={
            'Ces informations seront affichées dans votre page lieu, sur l’application pass Culture. ' +
            'Elles permettront aux bénéficiaires de vous contacter en cas de besoin.'
          }
        >
          <FormLayout.Row>
            <PhoneNumberInput name="phoneNumber" label="Téléphone" isOptional />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              name="email"
              label="Adresse email"
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
      )}
      <FormLayout.Section title="Notifications de réservations">
        <FormLayout.Row
          sideComponent={
            isVenueVirtual ? null : (
              <Callout>
                Cette adresse s’appliquera par défaut à toutes vos offres, vous
                pourrez la modifier à l’échelle de chaque offre.
              </Callout>
            )
          }
        >
          <TextInput
            name="bookingEmail"
            label="Adresse email"
            type="email"
            placeholder="email@exemple.com"
            isOptional={isVenueVirtual}
            disabled={isVenueVirtual}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Contact
