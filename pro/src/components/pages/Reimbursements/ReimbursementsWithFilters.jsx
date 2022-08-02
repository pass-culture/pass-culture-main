import './Reimbursement.scss'

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useRouteMatch } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'
import { Banner } from 'ui-kit'
import { sortByDisplayName } from 'utils/strings'

import Breadcrumb from '../../../new_components/Breadcrumb'

import ReimbursementsDetails from './ReimbursementsDetails/ReimbursementsDetails'
import ReimbursementsInvoices from './ReimbursementsInvoices/ReimbursementsInvoices'

export const STEP_ID_INVOICES = 'justificatifs'
export const STEP_ID_DETAILS = 'details'
export const mapPathToStep = {
  justificatifs: STEP_ID_INVOICES,
  details: STEP_ID_DETAILS,
}

const buildAndSortVenueFilterOptions = venues =>
  sortByDisplayName(
    venues.map(venue => ({
      id: venue.id,
      displayName: venue.isVirtual
        ? `${venue.offererName} - Offre numérique`
        : venue.publicName || venue.name,
    }))
  )

const Reimbursements = ({ currentUser }) => {
  const [isLoading, setIsLoading] = useState(true)
  const [venuesOptions, setVenuesOptions] = useState([])
  const [reimbursementPointsOptions, setReimbursementPointsOptions] = useState(
    []
  )
  const steps = [
    {
      id: STEP_ID_INVOICES,
      label: 'Justificatifs de remboursement',
      url: '/remboursements/justificatifs',
    },
    {
      id: STEP_ID_DETAILS,
      label: 'Détails des remboursements',
      url: '/remboursements/details',
    },
  ]

  const stepName = location.pathname.match(/[a-z]+$/)
  const activeStep = stepName ? mapPathToStep[stepName[0]] : STEP_ID_INVOICES

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
            displayName: item['name'],
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
          <Banner type="notification-info">
            En savoir plus sur
            <a
              className="bi-link tertiary-link"
              href="https://passculture.zendesk.com/hc/fr/articles/4411992051601"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site" />
              Les prochains remboursements
            </a>
            <a
              className="bi-link tertiary-link"
              href="https://passculture.zendesk.com/hc/fr/articles/4412007300369"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site" />
              Les modalités de remboursement
            </a>
          </Banner>
          <Breadcrumb activeStep={activeStep} steps={steps} styleType="tab" />
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

Reimbursements.propTypes = {
  currentUser: PropTypes.shape({
    isAdmin: PropTypes.bool.isRequired,
  }).isRequired,
}

export default Reimbursements
