import React from 'react'

import { SiretField } from 'components/layout/form/fields/SiretField'
import TextareaField from 'components/layout/form/fields/TextareaField'
import Toggle from 'ui-kit/Toggle'
import { useState } from 'react'

export interface SiretOrCommentInterface {
  isToggleDisabled?: boolean
  initialSiret?: string
  readOnly: boolean
  siren: string
  siretLabel: string
  updateIsSiretValued: (isSiretValued: boolean) => void
}

const SiretOrCommentFields = ({
  initialSiret,
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
      <Toggle
        label="Je veux créer un lieu avec SIRET"
        isActiveByDefault={isSiretSelected}
        isDisabled={readOnly || isToggleDisabled}
        handleClick={handleChange}
      ></Toggle>
      {isSiretSelected ? (
        <SiretField
          label={siretLabel}
          readOnly={readOnly}
          siren={siren}
          required={isSiretSelected}
        />
      ) : (
        <TextareaField
          label="Commentaire : "
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
