import { useFormContext } from 'react-hook-form'

import { getDataFromAddress } from 'apiClient/adresse/apiAdresse'
import { AdresseData } from 'apiClient/adresse/types'
import { getSiretData } from 'commons/core/Venue/getSiretData'
import { humanizeSiret, unhumanizeSiret } from 'commons/core/Venue/utils'
import {
  AutocompleteItemProps,
  handleAddressSelect,
} from 'commons/utils/handleAddressSelect'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { VenueSettingsFormValues } from '../types'

import { isSiretStartingWithSiren, valideSiretLength } from './validationSchema'

const serializeAdressData = (
  adressData: AdresseData[]
): AutocompleteItemProps[] => {
  return adressData.map((data) => ({
    value: data.id,
    label: data.label,
    disabled: false,
    extraData: {
      postalCode: data.postalCode,
      latitude: data.latitude,
      longitude: data.longitude,
      address: data.address,
      city: data.city,
      inseeCode: data.inseeCode,
    },
  }))
}

export type SiretOrCommentFieldsProps = {
  initialSiret?: string
  setIsFieldNameFrozen?: (isNameFrozen: boolean) => void
  siren?: string | null
}

export const SiretOrCommentFields = ({
  initialSiret = '',
  setIsFieldNameFrozen,
  siren,
}: SiretOrCommentFieldsProps): JSX.Element => {
  const hasSiret = initialSiret.length > 0
  const {
    setValue,
    register,
    formState: { errors },
  } = useFormContext<VenueSettingsFormValues>()

  const formatSiret = (siret: string) => {
    // remove character when it's not a number
    // this way we're sure that this field only accept number
    if (!(siret && /^[0-9]+$/.test(unhumanizeSiret(siret))) || !siret) {
      setValue('siret', humanizeSiret(siret))
    }
  }

  const onSiretChange = async (siret: string) => {
    formatSiret(siret)

    if (!valideSiretLength(siret) || !isSiretStartingWithSiren(siret, siren)) {
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
      setValue('name', response.values?.name ?? '')
      // getSuggestions pour récupérer les adresses
      const addressSuggestions = await getDataFromAddress(address)
      setValue('search-addressAutocomplete', address)
      setValue('addressAutocomplete', address)

      handleAddressSelect(setValue, serializeAdressData(addressSuggestions)[0])
    } catch {
      return
    }
  }

  return (
    <FormLayout.Row mdSpaceAfter>
      {hasSiret ? (
        <TextInput
          {...register('siret')}
          label="SIRET de la structure"
          type="text"
          onChange={(e) => onSiretChange(e.target.value)}
          error={errors.siret?.message}
          required={true}
        />
      ) : (
        <TextArea
          {...register('comment')}
          label="Commentaire de la structure sans SIRET"
          description="Par exemple : la structure est un équipement culturel qui n’appartient pas à mon entitée juridique."
          required
          maxLength={500}
          initialRows={6}
          error={errors.comment?.message}
        />
      )}
    </FormLayout.Row>
  )
}
