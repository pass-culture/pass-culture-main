import './Reimbursement.scss'

import React from 'react'
import { Route, Routes } from 'react-router-dom'

import {
  oldRoutesReimbursements,
  routesReimbursements,
} from 'app/AppRouter/subroutesReimbursements'
import { BannerReimbursementsInfo } from 'components/Banner'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import LinkVenueCallout from 'components/Callout/LinkVenueCallout'
import PendingBankAccountCallout from 'components/Callout/PendingBankAccountCallout'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import useActiveFeature from 'hooks/useActiveFeature'
import Titles from 'ui-kit/Titles/Titles'

const Reimbursements = (): JSX.Element => {
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const routes = isNewBankDetailsJourneyEnable
    ? routesReimbursements
    : oldRoutesReimbursements

  return (
    <>
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
    </>
  )
}

export default Reimbursements
