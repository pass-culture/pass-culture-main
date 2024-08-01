import { useField, useFormikContext } from 'formik'
import { useEffect } from 'react'

import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { getCoordsType, parseDms } from 'utils/coords'

import styles from './AddressManual.module.scss'

export const AddressManual = (): JSX.Element => {
  const [coords, coordsMeta] = useField('coords')

  const { setFieldValue } = useFormikContext()

  useEffect(() => {
    if (coords.value && !coordsMeta.error) {
      const coordsType = getCoordsType(coords.value)

      if (coordsType === 'DD') {
        const [latitude, longitude] = coords.value.split(', ')
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        setFieldValue('latitude', latitude)
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        setFieldValue('longitude', longitude)
      } else if (coordsType === 'DMS') {
        const [latitude, longitude] = coords.value.split(' ')
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        setFieldValue('latitude', parseDms(latitude))
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        setFieldValue('longitude', parseDms(longitude))
      } else {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        setFieldValue('latitude', '')
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        setFieldValue('longitude', '')
      }
    }
  }, [coords.value, coordsMeta.error, setFieldValue])

  return (
    <div className={styles['address-manual-wrapper']}>
      <FormLayout.Row>
        <TextInput label="Adresse postale" name="street" />
      </FormLayout.Row>
      <div className={styles['inline-fields']}>
        <FormLayout.Row inline className={styles['field-cp']}>
          <TextInput label="Code postal" name="postalCode" maxLength={5} />
        </FormLayout.Row>
        <FormLayout.Row inline className={styles['field-city']}>
          <TextInput label="Ville" name="city" />
        </FormLayout.Row>
      </div>
      <FormLayout.Row>
        <TextInput
          label="Coordonnées GPS"
          name="coords"
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
