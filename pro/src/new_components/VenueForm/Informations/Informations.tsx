import { useFormikContext } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'new_components/FormLayout'
import { InfoBox, Select, TextArea, TextInput } from 'ui-kit'

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

  return (
    <>
      <FormLayout.Section title="Informations du lieu">
        <FormLayout.Row>
          {!venueIsVirtual && (
            <SiretOrCommentFields
              initialSiret={initialValues.siret}
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
            label="Nom juridique"
            disabled={readOnly || isFieldNameFrozen}
          />
        </FormLayout.Row>
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text="C’est ce nom qui sera visible par le grand public et affiché sur votre justificatif de remboursement."
            />
          }
        >
          <TextInput name="publicName" label="Nom d’affichage" isOptional />
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
