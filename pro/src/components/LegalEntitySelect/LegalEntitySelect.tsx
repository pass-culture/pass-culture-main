import { useOffererNamesQuery } from '@/commons/hooks/swr/useOffererNamesQuery'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setAdminCurrentOfferer } from '@/commons/store/offerer/dispatchers/setAdminCurrentOfferer'
import {
  selectAdminCurrentOfferer,
  selectOffererNames,
} from '@/commons/store/offerer/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './LegalEntitySelect.module.scss'

export const LegalEntitySelect = (): JSX.Element | null => {
  const dispatch = useAppDispatch()
  const { isLoading } = useOffererNamesQuery()
  const offererNames = useAppSelector(selectOffererNames)

  const adminCurrentOfferer = useAppSelector(selectAdminCurrentOfferer)

  const value = adminCurrentOfferer?.id?.toString()

  const offererOptions =
    sortByLabel(
      offererNames?.map((item) => ({
        value: item['id'].toString(),
        label: item['name'],
      })) ?? []
    ) ?? []

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const offererId = Number(event.target.value)
    dispatch(setAdminCurrentOfferer(offererId))
  }

  return (
    <Select
      name="legal-entity"
      label="Entité juridique"
      options={offererOptions}
      className={styles['legal-entity-select']}
      value={value}
      onChange={handleChange}
      disabled={isLoading}
    />
  )
}
