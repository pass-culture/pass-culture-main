import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { getAdressDataAdapter } from 'components/Address/adapter'
import { handleAddressSelect } from 'components/Address/Address'
import FormLayout from 'components/FormLayout'
import { IVenueFormValues } from 'components/VenueForm/types'
import { humanizeSiret, unhumanizeSiret } from 'core/Venue'
import getSiretData from 'core/Venue/adapters/getSiretDataAdapter'
import { InfoBox, TextArea, TextInput } from 'ui-kit'
import Toggle from 'ui-kit/Toggle'

import { isSiretStartingWithSiren, valideSiretLength } from './validationSchema'

export interface SiretOrCommentInterface {
  isCreatedEntity: boolean
  initialSiret?: string
  isToggleDisabled?: boolean
  readOnly: boolean
  setIsFieldNameFrozen: (isNameFrozen: boolean) => void
  updateIsSiretValued: (isSiretValued: boolean) => void
  setIsSiretValued: (isSiretValued: boolean) => void
  siren: string
}

const SiretOrCommentFields = ({
  initialSiret = '',
  isCreatedEntity,
  isToggleDisabled = false,
  setIsFieldNameFrozen,
  readOnly,
  updateIsSiretValued,
  setIsSiretValued,
  siren,
}: SiretOrCommentInterface): JSX.Element => {
  const [isSiretSelected, setIsSiretSelected] = useState(
    !isToggleDisabled || initialSiret.length > 0
  )
  const { setFieldValue } = useFormikContext<IVenueFormValues>()

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

  const onSiretChange = async (siret: string) => {
    await formatSiret(siret)
    if (
      !valideSiretLength(siret) ||
      !isSiretStartingWithSiren(siret, siren) ||
      !isSiretSelected ||
      readOnly
    ) {
      setIsFieldNameFrozen(false)
      return
    }

    const response = await getSiretData(siret)

    /* istanbul ignore next: DEBT, TO FIX */
    if (!response?.isOk) {
      return
    }
    const address = `${response.payload.values?.address} ${response.payload.values?.postalCode} ${response.payload.values?.city}`
    setIsFieldNameFrozen(
      response != null &&
        response.payload.values != null &&
        response.payload.values.siret.length > 0
    )
    setFieldValue('name', response.payload.values?.name)
    // getSuggestions pour récupérer les adresses
    const responseAdressDataAdapter = await getAdressDataAdapter({
      search: address,
    })
    /* istanbul ignore next: DEBT, TO FIX */
    if (!responseAdressDataAdapter.isOk) {
      return
    }
    setFieldValue('search-addressAutocomplete', address)
    setFieldValue('addressAutocomplete', address)

    handleAddressSelect(setFieldValue, responseAdressDataAdapter.payload[0])
  }
  const [sideComponent, setSideComponent] = useState(<></>)
  useEffect(() => {
    setSideComponent(
      isSiretSelected ? (
        <InfoBox
          type="info"
          text="Le SIRET du lieu doit être lié au SIREN de votre structure. Attention, ce SIRET ne sera plus modifiable et ne pourra plus être utilisé pour un autre lieu."
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
          onChange={e => onSiretChange(e.target.value)}
        />
      ) : (
        <TextArea
          label="Commentaire du lieu sans SIRET"
          name="comment"
          placeholder="Par exemple : le lieu est un équipement culturel qui n’appartient pas à ma structure."
          isOptional={isSiretSelected}
          maxLength={500}
          countCharacters
          rows={6}
        />
      )}
    </>
  )
}

export default SiretOrCommentFields
