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
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'
import Spinner from 'ui-kit/Spinner/Spinner'

const Reimbursements = (): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const [isOfferersLoading, setIsOfferersLoading] = useState<boolean>(false)

  const { setOfferers, setSelectedOfferer, selectedOfferer } =
    useReimbursementContext()

  const routes = isNewBankDetailsJourneyEnabled
    ? routesReimbursements
    : oldRoutesReimbursements

  useEffect(() => {
    const fetchData = async () => {
      setIsOfferersLoading(true)
      try {
        const { offerersNames } = await api.listOfferersNames()
        setOfferers(offerersNames)
        if (offerersNames.length >= 1) {
          const offerer = await api.getOfferer(offerersNames[0].id)
          setSelectedOfferer(offerer)
        }
        setIsOfferersLoading(false)
      } catch (error) {
        setIsOfferersLoading(false)
      }
    }
    if (isNewBankDetailsJourneyEnabled) {
      fetchData()
    }
  }, [])

  if (isOfferersLoading && isNewBankDetailsJourneyEnabled) {
    return <Spinner />
  }

  return (
    <div className="reimbursements-container">
      <h1 className="title">Remboursements</h1>
      {!isNewBankDetailsJourneyEnabled && <BannerReimbursementsInfo />}
      <div className="banners">
        <AddBankAccountCallout titleOnly={true} offerer={selectedOfferer} />
        <PendingBankAccountCallout titleOnly={true} offerer={selectedOfferer} />
        <LinkVenueCallout titleOnly={true} offerer={selectedOfferer} />
      </div>
      <ReimbursementsBreadcrumb />
      <div>
        <Routes>
          {routes.map(({ path, element }) => (
            <Route key={path} path={path} element={element} />
          ))}
        </Routes>
      </div>
    </div>
  )
}

export default Reimbursements
