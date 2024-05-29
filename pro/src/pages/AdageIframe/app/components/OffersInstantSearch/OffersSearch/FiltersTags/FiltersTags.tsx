import { useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'

import { OfferAddressType } from 'apiClient/adage'
import fullClearIcon from 'icons/full-clear.svg'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import { Option } from 'pages/AdageIframe/app/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { SearchFormValues } from '../../OffersInstantSearch'
import { ADAGE_FILTERS_DEFAULT_VALUES } from '../../utils'
import { LocalisationFilterStates } from '../OffersSearch'

import styles from './FiltersTags.module.scss'

interface FiltersTagsProps {
  domainsOptions: Option<number>[]
  localisationFilterState: LocalisationFilterStates
  setLocalisationFilterState: (state: LocalisationFilterStates) => void
  resetForm: () => void
}

const createTag = (label: string, onClose: () => void) => {
  if (!label) {
    return null
  }
  return (
    <button
      className={styles['adage-tag']}
      onClick={() => onClose()}
      title={'Supprimer ' + label}
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
}: FiltersTagsProps) => {
  const { values, setFieldValue, handleSubmit } =
    useFormikContext<SearchFormValues>()

  const getOfferAdressTypeTag = () => {
    if (values.eventAddressType === OfferAddressType.OTHER) {
      return <></>
    }
    const label =
      values.eventAddressType === OfferAddressType.OFFERER_VENUE
        ? 'Sortie chez un partenaire culturel'
        : 'Intervention d’un partenaire culturel dans mon établissement'

    return createTag(label, () => {
      void setFieldValue('eventAddressType', OfferAddressType.OTHER)
      setLocalisationFilterState(LocalisationFilterStates.NONE)
      handleSubmit()
    })
  }
  const getGeoLocalisationTag = () => {
    if (localisationFilterState !== LocalisationFilterStates.GEOLOCATION) {
      return null
    }
    return createTag(
      `Localisation des partenaires : > à ${values.geolocRadius} km`,
      () => {
        void setFieldValue('geolocRadius', 50)
        setLocalisationFilterState(LocalisationFilterStates.NONE)
        handleSubmit()
      }
    )
  }

  const getVenueTag = () => {
    if (!values.venue) {
      return null
    }
    const venueDisplayName = `Lieu :  ${
      values.venue.publicName || values.venue.name
    }`
    return createTag(venueDisplayName, async () => {
      await setFieldValue('venue', null)
      handleSubmit()
    })
  }

  return (
    <div className={styles.container}>
      {getVenueTag()}
      {getOfferAdressTypeTag()}
      {getGeoLocalisationTag()}
      {values.academies.map((academy) =>
        createTag(academy, async () => {
          if (values.academies.length === 1) {
            setLocalisationFilterState(LocalisationFilterStates.NONE)
          }
          await setFieldValue(
            'academies',
            values.academies.filter((x) => x !== academy)
          )
          handleSubmit()
        })
      )}
      {values.departments.map((department) =>
        createTag(
          departmentOptions.find((dpt) => dpt.value === department)?.label ||
            '',
          async () => {
            if (values.departments.length === 1) {
              setLocalisationFilterState(LocalisationFilterStates.NONE)
            }
            await setFieldValue(
              'departments',
              values.departments.filter((x) => x !== department)
            )
            handleSubmit()
          }
        )
      )}
      {values.domains.map((domain) =>
        createTag(
          domainsOptions.find((dmn) => dmn.value === Number(domain))?.label ||
            '',
          async () => {
            await setFieldValue(
              'domains',
              values.domains.filter((x) => x !== domain)
            )
            handleSubmit()
          }
        )
      )}
      {values.students.map((student) =>
        createTag(student, async () => {
          await setFieldValue(
            'students',
            values.students.filter((x) => x !== student)
          )
          handleSubmit()
        })
      )}

      {values.formats.map((format) =>
        createTag(format, async () => {
          await setFieldValue(
            'formats',
            values.formats.filter((x) => x !== format)
          )
          handleSubmit()
        })
      )}
      {
        // TODO : We should use a custom isEqual instead of lodash one
        !isEqual(values, ADAGE_FILTERS_DEFAULT_VALUES) && (
          <Button
            onClick={resetForm}
            icon={fullRefreshIcon}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </Button>
        )
      }
    </div>
  )
}
