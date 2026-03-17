import { type FieldErrors, useFormContext } from 'react-hook-form'

import type {
  AddressFormValues,
  FlatAddressFormValues,
  LocationFormValues,
} from '@/commons/core/shared/types'
import { checkCoords, getCoordsType, parseDms } from '@/commons/utils/coords'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './AddressManual.module.scss'

interface AddressManualProps {
  readOnlyFields?: string[]
  gpsCalloutMessage?: string
  prefix?: '' | 'location.' | 'address.'
}

function getError(
  prefix: string,
  errors: FieldErrors<
    FlatAddressFormValues | AddressFormValues | LocationFormValues
  >,
  field:
    | keyof FlatAddressFormValues
    | keyof AddressFormValues
    | keyof LocationFormValues
) {
  if (prefix === 'location.') {
    // @ts-expect-error
    return (errors as FieldErrors<LocationFormValues>)?.location?.[field]
      ?.message
  } else if (prefix === 'address.') {
    // @ts-expect-error
    return (errors as FieldErrors<AddressFormValues>)?.address?.[field]?.message
  } else {
    // @ts-expect-error
    return errors?.[field]?.message
  }
}
export const AddressManual = ({
  readOnlyFields = [],
  gpsCalloutMessage,
  prefix = '',
}: AddressManualProps): JSX.Element => {
  const methods = useFormContext<
    FlatAddressFormValues | AddressFormValues | LocationFormValues
  >()

  const coords = methods.watch(`${prefix}coords`)

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

    methods.setValue(`${prefix}latitude`, latitude)
    methods.setValue(`${prefix}longitude`, longitude)
    methods.trigger(`${prefix}coords`)
  }

  return (
    <div className={styles['address-manual-wrapper']}>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Adresse postale"
          maxCharactersCount={200}
          disabled={readOnlyFields.includes('street')}
          {...methods.register(`${prefix}street`)}
          error={getError(prefix, methods.formState.errors, 'street')}
          required
        />
      </FormLayout.Row>
      <FormLayout.Row inline className={styles['inline-fields']} mdSpaceAfter>
        <div className={styles['field-cp']}>
          <TextInput
            label="Code postal"
            maxCharactersCount={5}
            disabled={readOnlyFields.includes('postalCode')}
            {...methods.register(`${prefix}postalCode`)}
            error={getError(prefix, methods.formState.errors, 'postalCode')}
            required
          />
        </div>
        <div className={styles['field-city']}>
          <TextInput
            label="Ville"
            disabled={readOnlyFields.includes('city')}
            maxCharactersCount={50}
            {...methods.register(`${prefix}city`)}
            error={getError(prefix, methods.formState.errors, 'city')}
            required
          />
        </div>
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Coordonnées GPS"
          type="text"
          description={`Exemple : 48.853320, 2.348979 ou 48°51'12.0"N 2°20'56.3"E`}
          disabled={readOnlyFields.includes('coords')}
          {...methods.register(`${prefix}coords`)}
          onBlur={onCoordsBlur}
          error={getError(prefix, methods.formState.errors, 'coords')}
          required
        />
      </FormLayout.Row>

      {coords && checkCoords(coords) && (
        <div className={styles['callout']}>
          <Banner
            title="Vérification de localisation"
            actions={[
              {
                href: `https://google.com/maps/place/${decodeURIComponent(coords)}`,
                label: 'Contrôlez la précision de vos coordonnées GPS.',
                isExternal: true,
                icon: fullLinkIcon,
                iconAlt: 'Nouvelle fenêtre',
                type: 'link',
              },
            ]}
          />
        </div>
      )}

      <div className={styles['callout']}>
        <Banner
          title="Coordonnées GPS importantes"
          variant={BannerVariants.WARNING}
          description={
            gpsCalloutMessage ??
            "Les coordonnées GPS permettent aux jeunes de géolocaliser votre offre dans l'application."
          }
        />
      </div>
    </div>
  )
}
