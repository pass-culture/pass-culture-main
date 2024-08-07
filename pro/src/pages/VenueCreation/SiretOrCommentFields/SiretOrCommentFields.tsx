import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { apiAdresse } from 'apiClient/adresse/apiAdresse'
import { handleAddressSelect } from 'components/Address/Address'
import { serializeAdressData } from 'components/Address/serializer'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { getSiretData } from 'core/Venue/getSiretData'
import { humanizeSiret, unhumanizeSiret } from 'core/Venue/utils'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { Toggle } from 'ui-kit/Toggle/Toggle'

import { isSiretStartingWithSiren, valideSiretLength } from './validationSchema'

export type SiretOrCommentFieldsProps = {
  isCreatedEntity: boolean
  initialSiret?: string
  isToggleDisabled?: boolean
  setIsFieldNameFrozen?: (isNameFrozen: boolean) => void
  updateIsSiretValued: (isSiretValued: boolean) => void
  siren?: string | null
}

export const SiretOrCommentFields = ({
  initialSiret = '',
  isCreatedEntity,
  isToggleDisabled = false,
  setIsFieldNameFrozen,
  updateIsSiretValued,
  siren,
}: SiretOrCommentFieldsProps): JSX.Element => {
  const [isSiretSelected, setIsSiretSelected] = useState(
    !isToggleDisabled || initialSiret.length > 0
  )
  const { setFieldValue } = useFormikContext<VenueCreationFormValues>()

  /* istanbul ignore next: DEBT, TO FIX */
  const handleToggleClick = () => {
    if (isSiretSelected && setIsFieldNameFrozen) {
      setIsFieldNameFrozen(false)
    }
    updateIsSiretValued(!isSiretSelected)
    setIsSiretSelected(!isSiretSelected)
  }

  const formatSiret = async (siret: string) => {
    // remove character when it's not a number
    // this way we're sure that this field only accept number
    if ((siret && /^[0-9]+$/.test(unhumanizeSiret(siret))) || !siret) {
      await setFieldValue('siret', humanizeSiret(siret))
    }
  }

  const onSiretChange = async (siret: string) => {
    await formatSiret(siret)
    if (
      !valideSiretLength(siret) ||
      !isSiretStartingWithSiren(siret, siren) ||
      !isSiretSelected
    ) {
      setIsFieldNameFrozen && setIsFieldNameFrozen(false)
      return
    }

    try {
      const response = await getSiretData(siret)

      /* istanbul ignore next: DEBT, TO FIX */
      const address = `${response.values?.address} ${response.values?.postalCode} ${response.values?.city}`
      setIsFieldNameFrozen &&
        setIsFieldNameFrozen(
          response.values !== undefined && response.values.siret.length > 0
        )
      await setFieldValue('name', response.values?.name)
      // getSuggestions pour récupérer les adresses
      const adressSuggestions = await apiAdresse.getDataFromAddress(address)
      await setFieldValue('search-addressAutocomplete', address)
      await setFieldValue('addressAutocomplete', address)

      handleAddressSelect(
        setFieldValue,
        serializeAdressData(adressSuggestions)[0]
      )
    } catch {
      return
    }
  }
  const [sideComponent, setSideComponent] = useState(<></>)
  useEffect(() => {
    setSideComponent(
      isSiretSelected ? (
        <InfoBox>
          Le SIRET du lieu doit être lié au SIREN de votre structure. Attention,
          ce SIRET ne sera plus modifiable et ne pourra plus être utilisé pour
          un autre lieu.
        </InfoBox>
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
            isDisabled={isToggleDisabled}
            handleClick={handleToggleClick}
          />
        </FormLayout.Row>
      )}
      {isSiretSelected ? (
        <TextInput
          name="siret"
          label="SIRET du lieu"
          type="text"
          onChange={(e) => onSiretChange(e.target.value)}
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
