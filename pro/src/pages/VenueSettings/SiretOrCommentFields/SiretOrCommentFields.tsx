import { useFormikContext } from 'formik'
import { useState } from 'react'

import { getDataFromAddress } from 'apiClient/adresse/apiAdresse'
import { getSiretData } from 'commons/core/Venue/getSiretData'
import { humanizeSiret, unhumanizeSiret } from 'commons/core/Venue/utils'
import { handleAddressSelect } from 'components/Address/Address'
import { serializeAdressData } from 'components/Address/serializer'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { Toggle } from 'ui-kit/Toggle/Toggle'

import { VenueSettingsFormValues } from '../types'

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
  const { setFieldValue } = useFormikContext<VenueSettingsFormValues>()

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
      setIsFieldNameFrozen?.(false)
      return
    }

    try {
      const response = await getSiretData(siret)

      /* istanbul ignore next: DEBT, TO FIX */
      const address = `${response.values?.address} ${response.values?.postalCode} ${response.values?.city}`
      setIsFieldNameFrozen?.(
        response.values !== undefined && response.values.siret.length > 0
      )
      await setFieldValue('name', response.values?.name)
      // getSuggestions pour récupérer les adresses
      const addressSuggestions = await getDataFromAddress(address)
      await setFieldValue('search-addressAutocomplete', address)
      await setFieldValue('addressAutocomplete', address)

      handleAddressSelect(
        setFieldValue,
        serializeAdressData(addressSuggestions)[0]
      )
    } catch {
      return
    }
  }

  return (
    <>
      {isCreatedEntity && (
        <FormLayout.Row
          sideComponent={
            isSiretSelected ? (
              <InfoBox>
                Le SIRET de la structure doit être lié au SIREN de votre entitée
                juridique. Attention, ce SIRET ne sera plus modifiable et ne
                pourra plus être utilisé pour une autre structure.
              </InfoBox>
            ) : (
              <></>
            )
          }
        >
          <Toggle
            label="Cette structure possède un SIRET"
            isActiveByDefault={isSiretSelected}
            isDisabled={isToggleDisabled}
            handleClick={handleToggleClick}
          />
        </FormLayout.Row>
      )}
      {isSiretSelected ? (
        <TextInput
          name="siret"
          label="SIRET de la structure"
          type="text"
          onChange={(e) => onSiretChange(e.target.value)}
        />
      ) : (
        <TextArea
          label="Commentaire de la structure sans SIRET"
          name="comment"
          description="Par exemple : la structure est un équipement culturel qui n’appartient pas à mon entitée juridique."
          isOptional={isSiretSelected}
          maxLength={500}
          rows={6}
        />
      )}
    </>
  )
}
