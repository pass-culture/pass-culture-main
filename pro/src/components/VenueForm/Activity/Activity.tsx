import React from 'react'

import FormLayout from 'components/FormLayout'
import { SelectOption } from 'custom_types/form'
import { Select, TextArea } from 'ui-kit'

export interface ActivityProps {
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  isVenueVirtual?: boolean
  isCreatingVenue: boolean
  isNewOnboardingActive: boolean
}

const Activity = ({
  venueTypes,
  venueLabels,
  isCreatingVenue,
  isVenueVirtual = false,
  isNewOnboardingActive,
}: ActivityProps) => {
  return (
    <>
      <FormLayout.Section
        title="Activité"
        description={
          isVenueVirtual
            ? undefined
            : 'Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu.'
        }
      >
        <FormLayout.Row>
          <Select
            options={[
              {
                value: '',
                label: 'Sélectionnez celui qui correspond à votre lieu',
              },
              ...venueTypes,
            ]}
            name="venueType"
            label={
              isNewOnboardingActive ? 'Activité principale' : 'Type de lieu'
            }
            disabled={isVenueVirtual}
          />
        </FormLayout.Row>
        {!isCreatingVenue && !isVenueVirtual && (
          <>
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
                label="Label du ministère de la Culture ou du Centre national du cinéma et de l'image animée"
                isOptional
              />
            </FormLayout.Row>
          </>
        )}
      </FormLayout.Section>
    </>
  )
}

export default Activity
