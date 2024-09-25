import { useTranslation } from 'react-i18next'

import fullDownIcon from 'icons/full-down.svg'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import styles from './Headeri18nDropdown.module.scss'

export const Headeri18nDropdown = () => {
  const { t, i18n } = useTranslation('common')

  const handleChangeLanguage = async (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const selectedLanguage = e.target.value

    if (localStorageAvailable()) {
      localStorage.setItem('i18nextLng', selectedLanguage)
    }

    await i18n.changeLanguage(e.target.value)
  }

  const supportedLanguages = i18n.options.supportedLngs || []
  const i18nOptions = supportedLanguages
    .filter((lng) => lng !== 'cimode' || process.env.NODE_ENV !== 'production')
    .map((lng) => {
      return {
        label: t(`language.${lng}`),
        value: lng,
      }
    })

  return (
    <SelectInput
      name="i18n"
      options={i18nOptions}
      value={i18n.language}
      onChange={handleChangeLanguage}
      className={styles['i18n-dropdown']}
      icon={fullDownIcon}
      iconClassName={styles['i18n-dropdown-icon']}
    />
  )
}
