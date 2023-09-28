import './Reimbursement.scss'

import React, { useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  oldRoutesReimbursements,
  routesReimbursements,
} from 'app/AppRouter/subroutesReimbursements'
import { BannerReimbursementsInfo } from 'components/Banner'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import LinkVenueCallout from 'components/Callout/LinkVenueCallout'
import PendingBankAccountCallout from 'components/Callout/PendingBankAccountCallout'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import {
  useReimbursementContext,
  ReimbursementContextProvider,
} from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'
import Spinner from 'ui-kit/Spinner/Spinner'
import Titles from 'ui-kit/Titles/Titles'

const Reimbursements = (): JSX.Element => {
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const [isOfferersLoading, setIsOfferersLoading] = useState<boolean>(false)

  const { setOfferers, setSelectedOfferer } = useReimbursementContext()

  const routes = isNewBankDetailsJourneyEnable
    ? routesReimbursements
    : oldRoutesReimbursements

  useEffect(() => {
    const fetchData = async () => {
      setIsOfferersLoading(true)
      try {
        const { offerersNames } = await api.listOfferersNames()
        if (offerersNames) {
          setOfferers(offerersNames)
          const offerer = await api.getOfferer(offerersNames[0].id)
          if (offerer) {
            setSelectedOfferer(offerer)
          }
        }
        setIsOfferersLoading(false)
      } catch (error) {
        setIsOfferersLoading(false)
      }
    }
    if (isNewBankDetailsJourneyEnable) {
      fetchData()
    }
  }, [])

  if (isOfferersLoading && isNewBankDetailsJourneyEnable) {
    return <Spinner />
  }

  return (
    <ReimbursementContextProvider>
      <Titles title="Remboursements" />
      <>
        {/* TODO: displaying condition when offerer is available here. (Done in another branch)*/}
        <AddBankAccountCallout titleOnly={true} />
        {/* TODO: displaying condition when offerer is available here. (Done in another branch)*/}
        <LinkVenueCallout titleOnly={true} />
        {/* TODO: displaying condition when offerer is available here. (Done in another branch)*/}
        <PendingBankAccountCallout titleOnly={true} />

        {!isNewBankDetailsJourneyEnable && <BannerReimbursementsInfo />}

        <ReimbursementsBreadcrumb />
        <Routes>
          {routes.map(({ path, element }) => (
            <Route key={path} path={path} element={element} />
          ))}
        </Routes>
      </>
    </ReimbursementContextProvider>
  )
}

export default Reimbursements
