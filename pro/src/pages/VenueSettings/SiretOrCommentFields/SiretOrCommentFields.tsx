import { useFormContext } from 'react-hook-form'

import { isError } from '@/apiClient/helpers'
import { getSiretData } from '@/commons/core/Venue/getSiretData'
import { unhumanizeRidet, unhumanizeSiret } from '@/commons/core/Venue/utils'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import {
  isRidetStartingWithSiren,
  isSiretStartingWithSiren,
  valideSiretLength,
  validRidetLength,
} from './validationSchema'

export type SiretOrCommentFieldsProps = {
  setIsFieldNameFrozen?: (isNameFrozen: boolean) => void
  siren?: string | null
  formContext: VenueSettingsFormContext
}

export const SiretOrCommentFields = ({
  setIsFieldNameFrozen,
  siren,
  formContext,
}: SiretOrCommentFieldsProps): JSX.Element => {
  const {
    setValue,
    setError,
    register,
    watch,
    formState: { errors, defaultValues },
  } = useFormContext<VenueSettingsFormValues>()

  const hasSiret = (defaultValues?.siret ?? '').length > 0
  const formatSiret = (siret: string) => {
    if (formContext.isCaledonian) {
      const _unhumanizeRidet = unhumanizeRidet(siret)
      if (
        watch('siret').length === 0 ||
        _unhumanizeRidet.length >= 0 ||
        _unhumanizeRidet.length === 14
      ) {
        setValue('siret', _unhumanizeRidet)
      }
    } else {
      const _unhumanizedSiret = unhumanizeSiret(siret)
      if (
        watch('siret').length === 0 ||
        _unhumanizedSiret.length > 0 ||
        _unhumanizedSiret.length === 14
      ) {
        setValue('siret', _unhumanizedSiret)
      }
    }
  }

  const onSiretChange = async (siret: string) => {
    formatSiret(siret)

    let isValid =
      valideSiretLength(siret) && isSiretStartingWithSiren(siret, siren)
    if (formContext.isCaledonian) {
      isValid =
        validRidetLength(siret) && isRidetStartingWithSiren(siret, siren)
    }
    if (isValid) {
      setIsFieldNameFrozen?.(false)
      return
    }

    try {
      const response = await getSiretData(siret)

      if (!response.isDiffusible) {
        setError('siret', {
          type: 'siret',
          message:
            'Certaines informations de votre structure ne sont pas diffusibles. Veuillez contacter le support.',
        })
        return
      }

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
    } catch (_e) {
      if (isError(_e)) {
        setError('siret', {
          type: 'siret',
          message: _e.message,
        })
      }
    }
  }

  return (
    <FormLayout.Row mdSpaceAfter>
      {hasSiret ? (
        <TextInput
          {...register('siret')}
          label={`${formContext.isCaledonian ? 'RIDET' : 'SIRET'} de la structure`}
          onChange={(e) => onSiretChange(e.target.value)}
          error={errors.siret?.message}
          required
        />
      ) : (
        <TextArea
          {...register('comment')}
          label={`Commentaire de la structure sans ${formContext.isCaledonian ? 'RIDET' : 'SIRET'}`}
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
