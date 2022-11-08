import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import FormLayout from 'components/FormLayout'
import { IVenueFormValues } from 'components/VenueForm/types'
import { humanizeSiret, unhumanizeSiret } from 'core/Venue'
import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { InfoBox, TextArea, TextInput } from 'ui-kit'
import Toggle from 'ui-kit/Toggle'

export interface SiretOrCommentInterface {
  isCreatedEntity: boolean
  initialSiret?: string
  isToggleDisabled?: boolean
  readOnly: boolean
  setIsFieldNameFrozen: (isNameFrozen: boolean) => void
  updateIsSiretValued: (isSiretValued: boolean) => void
  setIsSiretValued: (isSiretValued: boolean) => void
}

const SiretOrCommentFields = ({
  initialSiret = '',
  isCreatedEntity,
  isToggleDisabled = false,
  setIsFieldNameFrozen,
  readOnly,
  updateIsSiretValued,
  setIsSiretValued,
}: SiretOrCommentInterface): JSX.Element => {
  const [isSiretSelected, setIsSiretSelected] = useState(
    !isToggleDisabled || initialSiret.length > 0
  )

  const { setFieldValue, values, errors, touched } =
    useFormikContext<IVenueFormValues>()

  /* istanbul ignore next: DEBT, TO FIX */
  const handleToggleClick = () => {
    if (isSiretSelected) {
      setIsFieldNameFrozen(false)
    }
    setIsSiretValued(!isSiretSelected)
    updateIsSiretValued(!isSiretSelected)
    setIsSiretSelected(!isSiretSelected)
  }

  const formatSiret = async (siret: string): Promise<void> => {
    // remove character when it's not a number
    // this way we're sure that this field only accept number
    if ((siret && /^[0-9]+$/.test(unhumanizeSiret(siret))) || !siret) {
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
    touched.siret &&
      getSiretDataFromApi().then(response => {
        if (response?.isOk) {
          setIsFieldNameFrozen(
            response != null &&
              response.payload.values != null &&
              response.payload.values.siret.length > 0
          )
          setFieldValue('name', response.payload.values?.name)
        }
      })
  }, [touched.siret, errors.siret, isSiretSelected])

  const [sideComponent, setSideComponent] = useState(<></>)
  useEffect(() => {
    setSideComponent(
      isSiretSelected ? (
        <InfoBox
          type="info"
          text="Le SIRET du lieu doit être lié au SIREN de votre structure. Attention, ce SIRET ne sera plus modifiable. "
        />
      ) : (
        <></>
      )
    )
  }, [isSiretSelected])

  return (
    <>
      {isCreatedEntity && (
        <FormLayout.Row sideComponent={sideComponent}>
          <Toggle
            label="Ce lieu possède un SIRET"
            isActiveByDefault={isSiretSelected}
            isDisabled={readOnly || isToggleDisabled}
            handleClick={handleToggleClick}
          />
        </FormLayout.Row>
      )}
      {isSiretSelected ? (
        <TextInput
          name="siret"
          label="SIRET du lieu"
          disabled={readOnly}
          type="text"
          onChange={e => formatSiret(e.target.value)}
        />
      ) : (
        <TextArea
          label="Commentaire du lieu sans SIRET"
          name="comment"
          placeholder="Par exemple : Le lieu est un équipement culturel donc je n’ai pas de SIRET"
          isOptional={isSiretSelected}
        />
      )}
    </>
  )
}

export default SiretOrCommentFields
