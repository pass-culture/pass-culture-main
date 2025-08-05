import { useFormContext } from 'react-hook-form'

import { getSiretData } from 'commons/core/Venue/getSiretData'
import { humanizeSiret, unhumanizeSiret } from 'commons/core/Venue/utils'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { valideSiretLength } from 'pages/VenueSettings/SiretOrCommentFields/validationSchema'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { VenueSettingsFormValues } from '../types'

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
    setError,
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

    if (
      !valideSiretLength(siret) /* || !isSiretStartingWithSiren(siret, siren)*/
    ) {
      setIsFieldNameFrozen?.(false)
      return
    }
    try {
      const response = await getSiretData(siret)

      /* istanbul ignore next: DEBT, TO FIX */
      const address = `${response.address?.street} ${response.address?.postalCode} ${response.address?.city}`
      setIsFieldNameFrozen?.(
        response !== undefined && response.siret.length > 0
      )
      setValue('name', response?.name ?? '')

      setValue('addressAutocomplete', address)
      setValue('street', response.address?.street ?? '')
      setValue('postalCode', response.address?.postalCode ?? '')
      setValue('city', response.address?.city ?? '')
      setValue('latitude', response.address?.latitude.toString() ?? '')
      setValue('longitude', response.address?.longitude.toString() ?? '')
      setValue('inseeCode', response.address?.inseeCode ?? '')
    } catch (e) {
      setError('siret', {
        type: 'siret',
        message: e.message,
      })
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
