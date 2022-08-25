import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { humanizeSiret, unhumanizeSiret } from 'core/Venue'
import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { IVenueFormValues } from 'new_components/VenueForm/types'
import { TextArea, TextInput } from 'ui-kit'
import Toggle from 'ui-kit/Toggle'

export interface SiretOrCommentInterface {
  isCreatedEntity: boolean
  initialSiret?: string
  isToggleDisabled?: boolean
  readOnly: boolean
  setIsFieldNameFrozen: (isNameFrozen: boolean) => void
  siretLabel: string
  updateIsSiretValued: (isSiretValued: boolean) => void
}

const SiretOrCommentFields = ({
  initialSiret = '',
  isCreatedEntity,
  isToggleDisabled = false,
  setIsFieldNameFrozen,
  readOnly,
  siretLabel,
  updateIsSiretValued,
}: SiretOrCommentInterface): JSX.Element => {
  const [isSiretSelected, setIsSiretSelected] = useState(
    !isToggleDisabled || initialSiret !== null
  )

  const { setFieldValue, values, errors } = useFormikContext<IVenueFormValues>()
  const handleToggleClick = () => {
    if (isSiretSelected) {
      setIsFieldNameFrozen(false)
    }
    updateIsSiretValued(!isSiretSelected)
    setIsSiretSelected(!isSiretSelected)
  }

  const formatSiret = async (siret: string): Promise<void> => {
    // remove character when when it's not a number
    // this way we're sure that this field only accept number
    if ((siret && Number(unhumanizeSiret(siret))) || !siret) {
      setFieldValue('siret', humanizeSiret(siret))
    }
  }

  useEffect(() => {
    const getSiretDataFromApi = async () => {
      if (!errors.siret && isSiretSelected && !readOnly) {
        return await getSiretData(values.siret)
      }
      setIsFieldNameFrozen(false)
      return null
    }
    getSiretDataFromApi().then(response => {
      if (response?.isOk) {
        setIsFieldNameFrozen(true)
        setFieldValue('name', response.payload.values?.name)
      }
    })
  }, [errors.siret, isSiretSelected])

  return (
    <>
      {isCreatedEntity && (
        <Toggle
          label="Je veux créer un lieu avec SIRET"
          isActiveByDefault={isSiretSelected}
          isDisabled={readOnly || isToggleDisabled}
          handleClick={handleToggleClick}
        />
      )}
      {isSiretSelected ? (
        <TextInput
          name="siret"
          label={siretLabel}
          readOnly={readOnly}
          type="text"
          onChange={e => formatSiret(e.target.value)}
        />
      ) : (
        <TextArea
          label="Commentaire du lieu sans SIRET :"
          name="comment"
          placeholder="Je suis un équipement culturel (ou autre) donc je n’ai pas de SIRET ou je n’ai pas la gestion de ce lieu, il accueille simplement une proposition...
          "
          isOptional={isSiretSelected}
        />
      )}
    </>
  )
}

export default SiretOrCommentFields
