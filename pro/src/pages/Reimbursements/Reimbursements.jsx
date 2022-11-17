import './Reimbursement.scss'

import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import { api } from 'apiClient/api'
import { LogRouteNavigation } from 'app/AppRouter/LogRouteNavigation'
import { BannerReimbursementsInfo } from 'components/Banner'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import useActiveFeature from 'hooks/useActiveFeature'
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
  const [reimbursementPointsOptions, setReimbursementPointsOptions] = useState(
    []
  )

  const isNewBankInformationCreation = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )

  const match = useRouteMatch()

  const loadVenues = useCallback(async () => {
    const venuesResponse = await getVenuesForOffererAdapter({
      activeOfferersOnly: true,
    })
    const selectOptions = buildAndSortVenueFilterOptions(venuesResponse.payload)
    setVenuesOptions(selectOptions)
    setIsLoading(false)
  }, [setVenuesOptions])

  const loadReimbursementPoints = useCallback(async () => {
    try {
      /* istanbul ignore next: TO FIX */
      const reimbursementPointsResponse = isNewBankInformationCreation
        ? await api.getReimbursementPoints()
        : await api.getBusinessUnits()
      setReimbursementPointsOptions(
        sortByDisplayName(
          reimbursementPointsResponse.map(item => ({
            id: item['id'].toString(),
            displayName: item['publicName'] || item['name'],
          }))
        )
      )
    } catch (err) {
      /* istanbul ignore next: TO FIX */
      // FIX ME
      // eslint-disable-next-line
      console.error(err)
    }
  }, [setReimbursementPointsOptions])

  const hasNoResults = !isLoading && !venuesOptions.length
  const hasResults = !isLoading && venuesOptions.length > 0

  useEffect(() => {
    loadReimbursementPoints()
    loadVenues()
  }, [loadVenues, loadReimbursementPoints])

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

          <Switch>
            <Route exact path={`${match.path}/justificatifs`}>
              <LogRouteNavigation
                route={{ title: 'Vos justificatifs de remboursements' }}
              >
                <ReimbursementsInvoices
                  reimbursementPointsOptions={reimbursementPointsOptions}
                  isCurrentUserAdmin={currentUser.isAdmin}
                />
              </LogRouteNavigation>
            </Route>
            <Route exact path={`${match.path}/details`}>
              <LogRouteNavigation
                route={{ title: 'Détails de vos remboursements' }}
              >
                <ReimbursementsDetails
                  isCurrentUserAdmin={currentUser.isAdmin}
                  loadVenues={loadVenues}
                  venuesOptions={venuesOptions}
                />
              </LogRouteNavigation>
            </Route>
          </Switch>
        </>
      )}
    </>
  )
}

export default Reimbursements
