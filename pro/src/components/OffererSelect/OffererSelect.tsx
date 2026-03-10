import { useOffererNamesQuery } from '@/commons/hooks/swr/useOffererNamesQuery'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureOffererNames } from '@/commons/store/offerer/selectors'
import { setSelectedAdminOffererById } from '@/commons/store/user/dispatchers/setSelectedAdminOffererById'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './OffererSelect.module.scss'

export const OffererSelect = (): JSX.Element | null => {
  const dispatch = useAppDispatch()
  const { isLoading } = useOffererNamesQuery()
  const offererNames = useAppSelector(ensureOffererNames)
  const selectedAdminOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )

  const value = selectedAdminOfferer?.id?.toString()

  const offererOptions =
    offererNames?.map((item) => ({
      value: item['id'].toString(),
      label: item['name'],
    })) ?? []

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const offererId = Number(event.target.value)
    dispatch(
      setSelectedAdminOffererById({
        offererId,
      })
    )
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
