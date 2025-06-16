import { useFormContext } from 'react-hook-form'

import { OfferAddressType } from 'apiClient/adage'
import { CollectiveLocationType } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import fullClearIcon from 'icons/full-clear.svg'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import { Option } from 'pages/AdageIframe/app/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { SearchFormValues } from '../../OffersInstantSearch'
import { areFiltersEmpty } from '../../utils'
import { LocalisationFilterStates } from '../OffersSearch'

import styles from './FiltersTags.module.scss'

interface FiltersTagsProps {
  domainsOptions: Option<number>[]
  localisationFilterState: LocalisationFilterStates
  setLocalisationFilterState: (state: LocalisationFilterStates) => void
  resetForm: () => void
  onSubmit: () => void
}

const createTag = (label: string, onClose: () => void) => {
  if (!label) {
    return null
  }
  return (
    <button
      className={styles['adage-tag']}
      onClick={() => onClose()}
      type="button"
      key={label}
    >
      {label}
      <SvgIcon
        className={styles['adage-tag-icon']}
        src={fullClearIcon}
        alt={`Supprimer ${label}`}
        width={'20'}
      />
    </button>
  )
}

export const FiltersTags = ({
  domainsOptions,
  localisationFilterState,
  setLocalisationFilterState,
  resetForm,
  onSubmit,
}: FiltersTagsProps) => {
  const form = useFormContext<SearchFormValues>()

  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const getOfferAdressTypeTag = () => {
    if (
      form.watch('eventAddressType') === OfferAddressType.OTHER &&
      form.watch('locationType') === CollectiveLocationType.TO_BE_DEFINED
    ) {
      return <></>
    }

    const label =
      form.watch('eventAddressType') === OfferAddressType.OFFERER_VENUE ||
      form.watch('locationType') === CollectiveLocationType.ADDRESS
        ? 'Sortie chez un partenaire culturel'
        : 'Intervention d’un partenaire culturel dans mon établissement'

    return createTag(label, () => {
      if (isCollectiveOaActive) {
        form.setValue('locationType', CollectiveLocationType.TO_BE_DEFINED)
      } else {
        form.setValue('eventAddressType', OfferAddressType.OTHER)
      }
      setLocalisationFilterState(LocalisationFilterStates.NONE)
      onSubmit()
    })
  }
  const getGeoLocalisationTag = () => {
    if (localisationFilterState !== LocalisationFilterStates.GEOLOCATION) {
      return null
    }
    return createTag(
      `Localisation des partenaires : < à ${form.watch('geolocRadius')} km`,
      () => {
        form.setValue('geolocRadius', 50)
        setLocalisationFilterState(LocalisationFilterStates.NONE)
        onSubmit()
      }
    )
  }

  const getVenueTag = () => {
    if (!form.watch('venue')) {
      return null
    }
    const venueDisplayName = `Lieu :  ${
      form.watch('venue')?.publicName || form.watch('venue')?.name
    }`
    return createTag(venueDisplayName, () => {
      form.setValue('venue', null)
      onSubmit()
    })
  }

  return (
    <div className={styles.container}>
      {getVenueTag()}
      {getOfferAdressTypeTag()}
      {getGeoLocalisationTag()}
      {form.watch('academies').map((academy) =>
        createTag(academy, () => {
          if (form.watch('academies').length === 1) {
            setLocalisationFilterState(LocalisationFilterStates.NONE)
          }
          form.setValue(
            'academies',
            form.watch('academies').filter((x) => x !== academy)
          )
          onSubmit()
        })
      )}
      {form.watch('departments').map((department) =>
        createTag(
          departmentOptions.find((dpt) => dpt.value === department)?.label ||
            '',
          () => {
            if (form.watch('departments').length === 1) {
              setLocalisationFilterState(LocalisationFilterStates.NONE)
            }
            form.setValue(
              'departments',
              form.watch('departments').filter((x) => x !== department)
            )
            onSubmit()
          }
        )
      )}
      {form.watch('domains').map((domain) =>
        createTag(
          domainsOptions.find((dmn) => dmn.value === Number(domain))?.label ||
            '',
          () => {
            form.setValue(
              'domains',
              form.watch('domains').filter((x) => x !== domain)
            )
            onSubmit()
          }
        )
      )}
      {form.watch('students').map((student) =>
        createTag(student, () => {
          form.setValue(
            'students',
            form.watch('students').filter((x) => x !== student)
          )
          onSubmit()
        })
      )}

      {form.watch('formats').map((format) =>
        createTag(format, () => {
          form.setValue(
            'formats',
            form.watch('formats').filter((x) => x !== format)
          )
          onSubmit()
        })
      )}
      {!areFiltersEmpty(form.watch(), isCollectiveOaActive) && (
        <Button
          onClick={resetForm}
          icon={fullRefreshIcon}
          variant={ButtonVariant.TERNARY}
          type="submit"
        >
          Réinitialiser les filtres
        </Button>
      )}
    </div>
  )
}
