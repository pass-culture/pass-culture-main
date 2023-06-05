import { useFormikContext } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'components/FormLayout'
import { InfoBox, TextInput } from 'ui-kit'

import { IVenueFormValues } from '..'

import SiretOrCommentFields from './SiretOrCommentFields'

export interface IInformations {
  isCreatedEntity: boolean
  readOnly: boolean
  updateIsSiretValued: (value: boolean) => void
  setIsSiretValued: (value: boolean) => void
  isVenueVirtual: boolean
  siren: string
  isNewOnboardingActive: boolean
}

const Informations = ({
  isCreatedEntity,
  readOnly,
  updateIsSiretValued,
  isVenueVirtual,
  setIsSiretValued,
  siren,
  isNewOnboardingActive,
}: IInformations) => {
  const { initialValues } = useFormikContext<IVenueFormValues>()
  const [isFieldNameFrozen, setIsFieldNameFrozen] = useState(false)

  return (
    <>
      <FormLayout.Section title="Informations du lieu">
        {!isVenueVirtual && (
          <FormLayout.Row>
            <SiretOrCommentFields
              initialSiret={initialValues.siret}
              readOnly={readOnly || !!initialValues.siret}
              isToggleDisabled={!isCreatedEntity}
              isCreatedEntity={isCreatedEntity}
              setIsFieldNameFrozen={setIsFieldNameFrozen}
              setIsSiretValued={setIsSiretValued}
              updateIsSiretValued={updateIsSiretValued}
              siren={siren}
            />
          </FormLayout.Row>
        )}
        <FormLayout.Row>
          <TextInput
            name="name"
            label={isNewOnboardingActive ? 'Raison sociale' : 'Nom juridique'}
            disabled={readOnly || isFieldNameFrozen || isVenueVirtual}
          />
        </FormLayout.Row>
        {!isVenueVirtual && (
          <FormLayout.Row
            sideComponent={
              <InfoBox>
                À remplir si différent{' '}
                {isNewOnboardingActive
                  ? 'de la raison sociale'
                  : 'du nom juridique'}
                . En le remplissant, c’est ce dernier qui sera visible du
                public.
              </InfoBox>
            }
          >
            <TextInput
              name="publicName"
              label={isNewOnboardingActive ? 'Nom public' : 'Nom d’affichage'}
              isOptional
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </>
  )
}

export default Informations
