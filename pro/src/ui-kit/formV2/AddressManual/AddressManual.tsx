import React from 'react'
import { useFormContext } from 'react-hook-form'

import { AddressFormValues } from 'commons/core/shared/types'
import { getCoordsType, parseDms } from 'commons/utils/coords'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './AddressManual.module.scss'

interface AddressManualProps {
  readOnlyFields?: string[]
  gpsCalloutMessage?: string
}

export const AddressManual = ({
  readOnlyFields = [],
  gpsCalloutMessage,
}: AddressManualProps): JSX.Element => {
  const {
    register,
    setValue,
    trigger,
    watch,
    formState: { errors },
  } = useFormContext<AddressFormValues>()

  const coords = watch('coords')
  const coordsError = errors.coords?.message

  const onCoordsBlur = async (event: React.FocusEvent<HTMLInputElement>) => {
    const newCoords = event.target.value
    setValue('coords', newCoords, { shouldValidate: true, shouldDirty: true })

    // Validate coords field before proceeding
    const valid = await trigger('coords')
    if (!valid) {
      return
    }

    let latitude = 0,
      longitude = 0

    const coordsType = getCoordsType(newCoords)

    if (coordsType === 'DD') {
      ;[latitude, longitude] = newCoords
        .split(',')
        .map((c) => c.trim())
        .map(Number)
    } else if (coordsType === 'DMS') {
      ;[latitude, longitude] = newCoords.split(' ').map((c) => parseDms(c))
    }

    setValue('latitude', latitude.toString(), {
      shouldValidate: true,
      shouldDirty: true,
    })
    setValue('longitude', longitude.toString(), {
      shouldValidate: true,
      shouldDirty: true,
    })
  }

  return (
    <div className={styles['address-manual-wrapper']}>
      <FormLayout.Row>
        <TextInput
          label="Adresse postale"
          {...register('street')}
          disabled={readOnlyFields.includes('street')}
          maxLength={200}
          error={errors.street?.message}
        />
      </FormLayout.Row>
      <FormLayout.Row inline className={styles['inline-fields']}>
        <TextInput
          label="Code postal"
          {...register('postalCode')}
          maxLength={5}
          className={styles['field-cp']}
          disabled={readOnlyFields.includes('postalCode')}
          error={errors.postalCode?.message}
        />
        <TextInput
          label="Ville"
          {...register('city')}
          className={styles['field-city']}
          disabled={readOnlyFields.includes('city')}
          maxLength={50}
          error={errors.city?.message}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          label="Coordonnées GPS"
          {...register('coords')}
          onBlur={onCoordsBlur}
          type="text"
          description={`Exemple : 48.853320, 2.348979 ou 48°51'12.0"N 2°20'56.3"E`}
          disabled={readOnlyFields.includes('coords')}
          error={coordsError}
        />
      </FormLayout.Row>

      {coords && !coordsError && (
        <Callout className={styles['callout']}>
          <ButtonLink
            to={`https://google.com/maps/place/${encodeURIComponent(coords)}`}
            variant={ButtonVariant.TERNARY}
            isExternal
            opensInNewTab
          >
            Vérifiez la localisation en cliquant ici
          </ButtonLink>
        </Callout>
      )}

      <Callout variant={CalloutVariant.WARNING} className={styles['callout']}>
        {gpsCalloutMessage ??
          'Les coordonnées GPS sont des informations à ne pas négliger. Elles vont permettre aux jeunes de pouvoir géolocaliser votre offre sur leur application.'}
      </Callout>
    </div>
  )
}
