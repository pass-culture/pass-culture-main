import React, { useState } from 'react'

import { SiretField } from 'components/layout/form/fields/SiretField'
import TextareaField from 'components/layout/form/fields/TextareaField'
import Toggle from 'ui-kit/Toggle'

export interface SiretOrCommentInterface {
  isCreatedEntity: boolean
  isToggleDisabled?: boolean
  initialSiret?: string
  readOnly: boolean
  siren: string
  siretLabel: string
  updateIsSiretValued: (isSiretValued: boolean) => void
}

const SiretOrCommentFields = ({
  initialSiret,
  isCreatedEntity,
  isToggleDisabled = false,
  readOnly,
  siretLabel,
  siren,
  updateIsSiretValued,
}: SiretOrCommentInterface): JSX.Element => {
  const [isSiretSelected, setIsSiretSelected] = useState(
    !isToggleDisabled || initialSiret !== null
  )
  const handleChange = () => {
    updateIsSiretValued(!isSiretSelected)
    setIsSiretSelected(!isSiretSelected)
  }
  const commentValidate = (comment: string) => {
    if (comment === undefined || (comment === '' && !isSiretSelected)) {
      return 'Ce champ est obligatoire'
    }

    return ''
  }

  return (
    <>
      {isCreatedEntity && (
        <Toggle
          label="Je veux créer un lieu avec SIRET"
          isActiveByDefault={isSiretSelected}
          isDisabled={readOnly || isToggleDisabled}
          handleClick={handleChange}
        />
      )}
      {isSiretSelected ? (
        <SiretField
          label={siretLabel}
          readOnly={readOnly}
          siren={siren}
          required={isSiretSelected}
        />
      ) : (
        <TextareaField
          label="Commentaire du lieu sans SIRET : "
          name="comment"
          placeholder="Je suis un équipement culturel (ou autre) donc je n’ai pas de SIRET ou je n’ai pas la gestion de ce lieu, il accueille simplement une proposition...
          "
          readOnly={readOnly}
          required={!isSiretSelected}
          rows={2}
          validate={commentValidate}
        />
      )}
    </>
  )
}

export default SiretOrCommentFields
