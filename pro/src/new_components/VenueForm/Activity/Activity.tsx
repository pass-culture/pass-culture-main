import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { InfoBox, Select, TextArea } from 'ui-kit'

export interface IActivity {
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
}

const Activity = ({ venueTypes, venueLabels }: IActivity) => {
  return (
    <>
      <FormLayout.Section
        title="Activité"
        description="Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu."
      >
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text="S’il s'agit ici de la création du lieu de votre siège social, sélectionnez “lieu administratif”."
              link={{
                text: 'En savoir plus',
                to: 'https://aide.passculture.app/hc/fr/articles/5411407159196--Acteurs-Culturels-Dans-quel-cas-et-comment-cr%C3%A9er-un-lieu-administratif-rattach%C3%A9-%C3%A0-ma-structure-',
                isExternal: true,
                'aria-label': 'en savoir plus sur le type de lieu',
                target: '_blank',
                rel: 'noopener noreferrer',
              }}
            />
          }
        >
          <Select
            options={[
              {
                value: '',
                label: 'Sélectionner celui qui correspond à votre lieu',
              },
              ...venueTypes,
            ]}
            name="venueType"
            label="Type de lieu"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextArea
            name="description"
            label="Description"
            placeholder="Par exemple : Mon établissement propose des spectacles, de l'improvisation..."
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
            label="Label du Ministère de la Culture ou du CNC"
            isOptional
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Activity
