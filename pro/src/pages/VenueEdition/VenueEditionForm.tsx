import { GetVenueResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import { Select, TextArea, TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import { Accessibility } from '../VenueCreation/Accessibility/Accessibility'
import { VenueFormActionBar } from '../VenueCreation/VenueFormActionBar'

interface VenueFormProps {
  venueLabels: SelectOption[]
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({ venueLabels, venue }: VenueFormProps) => {
  useScrollToFirstErrorAfterSubmit()

  return (
    <div>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />

        {!venue.isVirtual && (
          <FormLayout.Section
            title="À propos de votre activité"
            description={
              venue.isVirtual
                ? undefined
                : 'Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu.'
            }
          >
            <FormLayout.Row>
              <TextArea
                name="description"
                label="Description"
                placeholder="Par exemple : mon établissement propose des spectacles, de l’improvisation..."
                maxLength={1000}
                countCharacters
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <Select
                options={[
                  {
                    value: '',
                    label:
                      'Si votre lieu est labellisé précisez-le en le sélectionnant',
                  },
                  ...venueLabels,
                ]}
                name="venueLabel"
                label="Label du ministère de la Culture ou du Centre national du cinéma et de l’image animée"
                isOptional
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

        {!venue.isVirtual && <Accessibility isCreatingVenue={false} />}

        {!venue.isVirtual && (
          <FormLayout.Section
            title="Contact"
            description={
              'Ces informations seront affichées dans votre page lieu, sur l’application pass Culture. ' +
              'Elles permettront aux bénéficiaires de vous contacter en cas de besoin.'
            }
          >
            <FormLayout.Row>
              <PhoneNumberInput
                name="phoneNumber"
                label="Téléphone"
                isOptional
              />
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
      </FormLayout>

      <VenueFormActionBar isCreatingVenue={false} />
    </div>
  )
}
