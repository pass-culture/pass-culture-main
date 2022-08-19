import './Reimbursement.scss'

import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { BannerReimbursementsInfo } from 'new_components/Banner'
import { ReimbursementsBreadcrumb } from 'new_components/ReimbursementsBreadcrumb'
import * as pcapi from 'repository/pcapi/pcapi'
import { sortByDisplayName } from 'utils/strings'

import ReimbursementsDetails from './ReimbursementsDetails/ReimbursementsDetails'
import { ReimbursementsInvoices } from './ReimbursementsInvoices'

const buildAndSortVenueFilterOptions = venues =>
  sortByDisplayName(
    venues.map(venue => ({
      id: venue.id,
      displayName: venue.isVirtual
        ? `${venue.offererName} - Offre numérique`
        : venue.publicName || venue.name,
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
    try {
      const venuesResponse = await pcapi.getVenuesForOfferer({
        activeOfferersOnly: true,
      })
      const selectOptions = buildAndSortVenueFilterOptions(venuesResponse)
      setVenuesOptions(selectOptions)
      setIsLoading(false)
    } catch (err) {
      // FIX ME
      // eslint-disable-next-line
      console.error(err)
    }
  }, [setVenuesOptions])

  const loadReimbursementPoints = useCallback(async () => {
    try {
      const reimbursementPointsResponse = isNewBankInformationCreation
        ? await pcapi.getReimbursementPoints()
        : await pcapi.getBusinessUnits()
      setReimbursementPointsOptions(
        sortByDisplayName(
          reimbursementPointsResponse.map(item => ({
            id: item['id'].toString(),
            displayName: item['publicName'] ?? item['name'],
          }))
        )
      )
    } catch (err) {
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
      <PageTitle title="Vos remboursements" />
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
          <p>
            Les remboursements s’effectuent tous les 15 jours, rétroactivement
            suite à la validation d’une contremarque dans le guichet ou à la
            validation automatique des contremarques d’évènements. Cette page
            est automatiquement mise à jour à chaque remboursement.
          </p>
          <BannerReimbursementsInfo />

          <ReimbursementsBreadcrumb />

          <Switch>
            <Route exact path={`${match.path}/justificatifs`}>
              <ReimbursementsInvoices
                reimbursementPointsOptions={reimbursementPointsOptions}
                isCurrentUserAdmin={currentUser.isAdmin}
              />
            </Route>
            <Route exact path={`${match.path}/details`}>
              <ReimbursementsDetails
                isCurrentUserAdmin={currentUser.isAdmin}
                loadVenues={loadVenues}
                venuesOptions={venuesOptions}
              />
            </Route>
          </Switch>
        </>
      )}
    </>
  )
}

export default Reimbursements
