import { useField, useFormikContext } from 'formik'
import React from 'react'

import { AddressFormValues } from 'commons/core/shared/types'
import { getCoordsType, parseDms } from 'commons/utils/coords'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './AddressManual.module.scss'

interface AddressManualProps {
  readOnlyFields?: string[]
  gpsCalloutMessage?: string
}

export const AddressManual = ({
  readOnlyFields = [],
  gpsCalloutMessage,
}: AddressManualProps): JSX.Element => {
  const [coords, coordsMeta] = useField<string>('coords')

  const formik = useFormikContext<AddressFormValues>()

  const onCoordsBlur = async (event: React.ChangeEvent<HTMLInputElement>) => {
    formik.handleChange(event)
    await formik.setFieldTouched('coords', true, true)

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

    await formik.setFieldValue('latitude', latitude)
    await formik.setFieldValue('longitude', longitude)
  }

  return (
    <div className={styles['address-manual-wrapper']}>
      <FormLayout.Row>
        <TextInput
          label="Adresse postale"
          name="street"
          disabled={readOnlyFields.includes('street')}
          maxLength={200}
        />
      </FormLayout.Row>
      <FormLayout.Row inline className={styles['inline-fields']}>
        <TextInput
          label="Code postal"
          name="postalCode"
          maxLength={5}
          className={styles['field-cp']}
          disabled={readOnlyFields.includes('postalCode')}
        />
        <TextInput
          label="Ville"
          name="city"
          className={styles['field-city']}
          disabled={readOnlyFields.includes('city')}
          maxLength={50}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          label="Coordonnées GPS"
          name="coords"
          onBlur={onCoordsBlur}
          type="text"
          description={`Exemple : 48.853320, 2.348979 ou 48°51'12.0"N 2°20'56.3"E`}
          disabled={readOnlyFields.includes('coords')}
        />
      </FormLayout.Row>

      {coords.value && !coordsMeta.error && (
        <>
          <Callout variant={CalloutVariant.INFO} className={styles['callout']}>
            <ButtonLink
              to={`https://google.com/maps/place/${decodeURIComponent(coords.value)}`}
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
