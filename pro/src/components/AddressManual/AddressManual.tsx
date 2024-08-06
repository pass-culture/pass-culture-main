import { useField, useFormikContext } from 'formik'
import React from 'react'

import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { type IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { getCoordsType, parseDms } from 'utils/coords'

import styles from './AddressManual.module.scss'

export const AddressManual = (): JSX.Element => {
  const [coords, coordsMeta] = useField<string>('coords')

  const formik = useFormikContext<IndividualOfferFormValues>()

  const onCoordsBlur = async (event: React.ChangeEvent<HTMLInputElement>) => {
    formik.handleChange(event)
    await formik.setFieldTouched('coords', true, true)

    const newCoords = event.target.value
    let latitude = '',
      longitude = ''

    const coordsType = getCoordsType(newCoords)

    if (coordsType === 'DD') {
      ;[latitude, longitude] = newCoords.split(', ')
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
        <TextInput label="Adresse postale" name="street" />
      </FormLayout.Row>
      <FormLayout.Row inline className={styles['inline-fields']}>
        <TextInput
          label="Code postal"
          name="postalCode"
          maxLength={5}
          className={styles['field-cp']}
        />
        <TextInput label="Ville" name="city" className={styles['field-city']} />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          label="Coordonnées GPS"
          name="coords"
          onBlur={onCoordsBlur}
          type="text"
          description={`Exemple : 48.853320, 2.348979 ou 48°51'12.0"N 2°20'56.3"E`}
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
        Les coordonnées GPS sont des informations à ne pas négliger. Elles vont
        permettre aux jeunes de pouvoir géolocaliser votre offre sur leur
        application.
      </Callout>
    </div>
  )
}
