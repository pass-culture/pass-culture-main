import { useFormContext } from 'react-hook-form'

import { isError } from '@/apiClient/helpers'
import { getSiretData } from '@/commons/core/Venue/getSiretData'
import {
  humanizeSiret,
  isSiretStartingWithSiren,
  unhumanizeRidet,
  unhumanizeSiret,
  validSiretLength,
} from '@/commons/utils/siren'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../../commons/types'

export type SiretOrCommentFieldsProps = {
  setIsFieldNameFrozen?: (isNameFrozen: boolean) => void
  formContext: VenueSettingsFormContext
}

export const SiretOrCommentFields = ({
  setIsFieldNameFrozen,
  formContext,
}: SiretOrCommentFieldsProps): JSX.Element => {
  const {
    setValue,
    setError,
    register,
    formState: { errors },
  } = useFormContext<VenueSettingsFormValues>()

  const hasComment = !formContext.withSiret
  const hasRidet = formContext.isCaledonian

  const onSiretChange = async (siret: string) => {
    const cleanSiret = unhumanizeSiret(siret)
    setValue('siret', humanizeSiret(cleanSiret), {
      shouldDirty: true,
    })

    if (
      !validSiretLength(cleanSiret) ||
      !isSiretStartingWithSiren(cleanSiret, formContext.siren)
    ) {
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
      const address = `${response.location?.street} ${response.location?.postalCode} ${response.location?.city}`
      setIsFieldNameFrozen?.(
        response !== undefined && response.siret.length > 0
      )
      setValue('name', response?.name ?? '')

      setValue('addressAutocomplete', address)
      setValue('street', response.location?.street ?? '')
      setValue('postalCode', response.location?.postalCode ?? '')
      setValue('city', response.location?.city ?? '')
      setValue('latitude', response.location?.latitude.toString() ?? '')
      setValue('longitude', response.location?.longitude.toString() ?? '')
      setValue('inseeCode', response.location?.inseeCode ?? '')
    } catch (_e) {
      if (isError(_e)) {
        setError('siret', {
          type: 'siret',
          message: _e.message,
        })
      }
    }
  }

  const onRidetChange = (ridet: string) => {
    setValue('siret', unhumanizeRidet(ridet || '', false, false), {
      shouldDirty: true,
    })

    if (!errors.siret?.message) {
      setIsFieldNameFrozen?.(false)
    }
  }

  return (
    <FormLayout.Row mdSpaceAfter>
      {hasComment ? (
        <TextArea
          {...register('comment')}
          label={`Commentaire de la structure sans ${formContext.isCaledonian ? 'RIDET' : 'SIRET'}`}
          description="Par exemple : la structure est un équipement culturel qui n’appartient pas à mon entitée juridique."
          required
          maxLength={500}
          initialRows={6}
          error={errors.comment?.message}
        />
      ) : hasRidet ? (
        <TextInput
          {...register('siret')}
          label={`RIDET de la structure`}
          onChange={(e) => onRidetChange(e.target.value)}
          error={errors.siret?.message}
          required
        />
      ) : (
        <TextInput
          {...register('siret')}
          label={`SIRET de la structure`}
          onChange={async (e) => await onSiretChange(e.target.value)}
          error={errors.siret?.message}
          required
        />
      )}
    </FormLayout.Row>
  )
}
