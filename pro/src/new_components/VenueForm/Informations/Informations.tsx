import { useFormikContext } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'new_components/FormLayout'
import { Select, TextArea, TextInput } from 'ui-kit'

import { IVenueFormValues } from '..'

import SiretOrCommentFields from './SiretOrCommentFields'

export interface IInformations {
  isCreatedEntity: boolean
  readOnly: boolean
  updateIsSiretValued: (value: boolean) => void
  venueIsVirtual: boolean
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
}

const Informations = ({
  isCreatedEntity,
  readOnly,
  updateIsSiretValued,
  venueIsVirtual,
  venueTypes,
  venueLabels,
}: IInformations) => {
  const { initialValues } = useFormikContext<IVenueFormValues>()
  const [isFieldNameFrozen, setIsFieldNameFrozen] = useState(false)
  const siretLabel = isCreatedEntity ? 'SIRET de ce lieu' : 'SIRET'

  return (
    <>
      <FormLayout.Section title="Informations du lieu">
        <FormLayout.Row>
          {!venueIsVirtual && (
            <SiretOrCommentFields
              siretLabel={siretLabel}
              readOnly={readOnly || !!initialValues.siret}
              isToggleDisabled={!isCreatedEntity}
              isCreatedEntity={isCreatedEntity}
              setIsFieldNameFrozen={setIsFieldNameFrozen}
              updateIsSiretValued={updateIsSiretValued}
            />
          )}
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            name="name"
            label="Nom du lieu"
            readOnly={isFieldNameFrozen}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            name="publicName"
            label="Nom d'affichage du lieu"
            isOptional
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            name="mail"
            label="Adresse e-mail qui recevra les notifications de réservation"
            type="email"
            placeholder="email@exemple.com"
          />
        </FormLayout.Row>
        <FormLayout.Row>
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
        <FormLayout.Row>
          <TextArea
            name="description"
            label="Description"
            maxLength={1000}
            countCharacters
            isOptional
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}

export default Informations
