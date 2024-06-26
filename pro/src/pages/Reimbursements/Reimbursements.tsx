import React, { Dispatch, SetStateAction, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Outlet, useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { ReimbursementsTabs } from 'components/ReimbursementsTabs/ReimbursementsTabs'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import { updateSelectedOffererId } from 'store/user/reducer'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Reimbursement.module.scss'

export interface ReimbursementsContextProps {
  selectedOfferer: GetOffererResponseModel | null
  setSelectedOfferer: Dispatch<SetStateAction<GetOffererResponseModel | null>>
}

export const Reimbursements = (): JSX.Element => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const location = useLocation()
  const { structure } = queryParamsFromOfferer(location)
  const paramOffererId = isNewInterfaceActive ? selectedOffererId : structure

  const [isOfferersLoading, setIsOfferersLoading] = useState<boolean>(false)
  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)

  const dispatch = useDispatch()

  useEffect(() => {
    const fetchData = async () => {
      setIsOfferersLoading(true)
      try {
        const { offerersNames } = await api.listOfferersNames()
        if (offerersNames.length >= 1) {
          const offerer = await api.getOfferer(
            Number(paramOffererId) || selectedOffererId || offerersNames[0].id
          )

          setSelectedOfferer(offerer)

          localStorage.setItem(SAVED_OFFERER_ID_KEY, offerer.id.toString())
          dispatch(updateSelectedOffererId(offerer.id))
        }
        setIsOfferersLoading(false)
      } catch (error) {
        setIsOfferersLoading(false)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    fetchData()
  }, [paramOffererId])

  if (isOfferersLoading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className={styles['reimbursements-container']}>
        <h1 className={styles['title']}>Gestion financière</h1>
        <div>
          <ReimbursementsTabs selectedOfferer={selectedOfferer} />

          <Outlet context={{ selectedOfferer, setSelectedOfferer }} />
        </div>
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
