import './Reimbursement.scss'

import React, { useCallback, useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'

import { BannerReimbursementsInfo } from 'components/Banner'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import useCurrentUser from 'hooks/useCurrentUser'
import Icon from 'ui-kit/Icon/Icon'
import Spinner from 'ui-kit/Spinner/Spinner'
import Titles from 'ui-kit/Titles/Titles'
import { sortByDisplayName } from 'utils/strings'

import ReimbursementsDetails from './ReimbursementsDetails/ReimbursementsDetails'
import { ReimbursementsInvoices } from './ReimbursementsInvoices'

const buildAndSortVenueFilterOptions = venues =>
  sortByDisplayName(
    venues.map(venue => ({
      id: venue.id,
      displayName: venue.isVirtual
        ? `${venue.offererName} - Offre numérique`
        : /* istanbul ignore next: TO FIX */
          venue.publicName || venue.name,
    }))
  )

const Reimbursements = () => {
  const { currentUser } = useCurrentUser()
  const [isLoading, setIsLoading] = useState(true)
  const [venuesOptions, setVenuesOptions] = useState([])

  const loadVenues = useCallback(async () => {
    const venuesResponse = await getVenuesForOffererAdapter({
      activeOfferersOnly: true,
    })
    const selectOptions = buildAndSortVenueFilterOptions(venuesResponse.payload)
    setVenuesOptions(selectOptions)
    setIsLoading(false)
  }, [setVenuesOptions])

  const hasNoResults = !isLoading && !venuesOptions.length
  const hasResults = !isLoading && venuesOptions.length > 0

  useEffect(() => {
    loadVenues()
  }, [loadVenues])

  return (
    <>
      <Titles title="Remboursements" />
      {isLoading && <Spinner />}
      {hasNoResults && (
        <div className="no-refunds">
          <Icon alt="" svg="ico-no-bookings" />
          <span>Aucun remboursement à afficher</span>
        </div>
      )}
      {hasResults && (
        <>
          <BannerReimbursementsInfo />

          <ReimbursementsBreadcrumb />

          <Routes>
            <Route path="/justificatifs" element={<ReimbursementsInvoices />} />
            <Route
              path="/details"
              element={
                <ReimbursementsDetails
                  isCurrentUserAdmin={currentUser.isAdmin}
                  loadVenues={loadVenues}
                  venuesOptions={venuesOptions}
                />
              }
            />
          </Routes>
        </>
      )}
    </>
  )
}

export default Reimbursements
