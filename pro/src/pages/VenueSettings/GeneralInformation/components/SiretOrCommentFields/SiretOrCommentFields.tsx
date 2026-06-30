import { useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { isError } from '@/apiClient/helpers'
import { getSiretData } from '@/commons/core/Venue/utils/getSiretData'
import {
  humanizeSiret,
  isSiretStartingWithSiren,
  unhumanizeRidet,
  unhumanizeSiret,
  validSiretLength,
} from '@/commons/utils/siren'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
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
  const isOpenToPublic = formContext.isOpenToPublic
  const [currentSiret, setCurrentSiret] = useState<string | null>(
    formContext.siret ?? null
  )

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

      setIsFieldNameFrozen?.(
        response !== undefined && response.siret.length > 0
      )
      setValue('name', response?.name ?? '')

      if (isOpenToPublic === 'true') {
        setValue('addressAutocomplete', '')
        setValue('street', '')
        setValue('postalCode', '')
        setValue('city', '')
        setValue('latitude', '')
        setValue('longitude', '')
        setValue('inseeCode', '')
      }
      setCurrentSiret(cleanSiret)
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
    const cleanRidet = unhumanizeRidet(ridet || '', false, false)
    setValue('siret', cleanRidet, {
      shouldDirty: true,
    })
    setCurrentSiret(cleanRidet)

    if (!errors.siret?.message) {
      setIsFieldNameFrozen?.(false)
    }
  }

  return (
    <>
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
      {formContext.siret !== currentSiret && (
        <FormLayout.Row mdSpaceAfter>
          <Banner
            title="Vous avez changé de SIRET."
            description="Veuillez vérifier et mettre à jour vos informations avant de les enregistrer."
            variant={BannerVariants.WARNING}
          />
        </FormLayout.Row>
      )}
    </>
  )
}
