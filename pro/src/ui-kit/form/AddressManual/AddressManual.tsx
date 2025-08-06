import { useFormContext } from 'react-hook-form'

import { AddressFormValues } from '@/commons/core/shared/types'
import { getCoordsType, parseDms } from '@/commons/utils/coords'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import styles from './AddressManual.module.scss'

interface AddressManualProps {
  readOnlyFields?: string[]
  gpsCalloutMessage?: string
}

export const AddressManual = ({
  readOnlyFields = [],
  gpsCalloutMessage,
}: AddressManualProps): JSX.Element => {
  const methods = useFormContext<AddressFormValues>()

  const coords = methods.watch('coords')

  const onCoordsBlur = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newCoords = event.target.value

    let latitude = '',
      longitude = ''

    const coordsType = getCoordsType(newCoords)

    if (coordsType === 'DD') {
      ;[latitude, longitude] = newCoords.split(',').map((c) => c.trim())
    } else if (coordsType === 'DMS') {
      ;[latitude, longitude] = newCoords
        .split(' ')
        .map((c) => String(parseDms(c)))
    }

    methods.setValue('latitude', latitude)
    methods.setValue('longitude', longitude)
  }

  return (
    <div className={styles['address-manual-wrapper']}>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Adresse postale"
          disabled={readOnlyFields.includes('street')}
          maxLength={200}
          {...methods.register('street')}
          error={methods.formState.errors.street?.message}
          required
        />
      </FormLayout.Row>
      <FormLayout.Row inline className={styles['inline-fields']} mdSpaceAfter>
        <TextInput
          label="Code postal"
          maxLength={5}
          className={styles['field-cp']}
          disabled={readOnlyFields.includes('postalCode')}
          {...methods.register('postalCode')}
          error={methods.formState.errors.postalCode?.message}
          required
        />
        <TextInput
          label="Ville"
          className={styles['field-city']}
          disabled={readOnlyFields.includes('city')}
          maxLength={50}
          {...methods.register('city')}
          error={methods.formState.errors.city?.message}
          required
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Coordonnées GPS"
          type="text"
          description={`Exemple : 48.853320, 2.348979 ou 48°51'12.0"N 2°20'56.3"E`}
          disabled={readOnlyFields.includes('coords')}
          {...methods.register('coords')}
          onBlur={onCoordsBlur}
          error={methods.formState.errors.coords?.message}
          required
        />
      </FormLayout.Row>

      {coords && (
        <>
          <Callout variant={CalloutVariant.INFO} className={styles['callout']}>
            <ButtonLink
              to={`https://google.com/maps/place/${decodeURIComponent(coords)}`}
              variant={ButtonVariant.TERNARY}
              isExternal
              opensInNewTab
            >
              Vérifiez la localisation en cliquant ici
            </ButtonLink>
          </Callout>
        </>
      )}

      <Callout variant={CalloutVariant.WARNING} className={styles['callout']}>
        {gpsCalloutMessage ??
          'Les coordonnées GPS sont des informations à ne pas négliger. Elles vont permettre aux jeunes de pouvoir géolocaliser votre offre sur leur application.'}
      </Callout>
    </div>
  )
}
