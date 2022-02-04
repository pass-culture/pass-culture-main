import PropTypes from 'prop-types'
import React, { useEffect, useMemo, useState, useCallback } from 'react'
import { NavLink } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'

import ApiKey from './ApiKey/ApiKey'
import BankInformation from './BankInformation/BankInformation'
import { Offerer } from './Offerer'
import VenuesContainer from './Venues/VenuesContainer'

const OffererDetails = ({ offererId }) => {
  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const [offerer, setOfferer] = useState(null)
  const [physicalVenues, setPhysicalVenues] = useState([])
  const [businessUnitList, setBusinessUnitList] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const hasInvalidBusinessUnits = useMemo(() => {
    if (!isBankInformationWithSiretActive) return false
    if (!offerer) return false
    return (
      businessUnitList.filter(businessUnit => !businessUnit.siret).length > 0
    )
  }, [offerer, businessUnitList, isBankInformationWithSiretActive])

  const resetOfferer = useCallback(id => {
    setOfferer({ id: id, managedVenues: [] })
    setBusinessUnitList([])
    setPhysicalVenues([])
  }, [])

  const loadOfferer = useCallback(
    async id => {
      try {
        const receivedOfferer = await pcapi.getOfferer(id)
        setOfferer(new Offerer(receivedOfferer))
        setPhysicalVenues(
          receivedOfferer.managedVenues.filter(venue => !venue.isVirtual)
        )
      } catch (error) {
        if (error.status === HTTP_STATUS.FORBIDDEN) {
          resetOfferer(id)
        }
      }
    },
    [resetOfferer]
  )

  useEffect(() => {
    async function initializeOfferer(id) {
      try {
        await loadOfferer(id)
        const receivedBusinessUnitList = await pcapi.getBusinessUnits(id)
        setBusinessUnitList(receivedBusinessUnitList)
      } catch (error) {
        if (error.status === HTTP_STATUS.FORBIDDEN) {
          resetOfferer(id)
        }
      }
      setIsLoading(false)
    }

    offererId && initializeOfferer(offererId)
  }, [offererId, loadOfferer, resetOfferer])

  if (isLoading) {
    return (
      <div className="h-card h-card-secondary h-card-placeholder">
        <div className="h-card-inner">
          <Spinner />
        </div>
      </div>
    )
  }

  return (
    <div className="offerer-page">
      <NavLink
        className="back-button has-text-primary"
        to={`/accueil?structure=${offerer.id}`}
      >
        <Icon svg="ico-back" />
        Accueil
      </NavLink>
      <PageTitle title="Détails de votre structure" />
      <Titles subtitle={offerer.name} title="Structure" />
      <p className="op-teaser">
        Détails de la structure rattachée, des lieux et des fournisseurs de ses
        offres.
      </p>
      <div className="section op-content-section">
        <h2 className="main-list-title">Informations structure</h2>
        <div className="op-detail">
          <span>{'SIREN : '}</span>
          <span>{offerer.formattedSiren}</span>
        </div>
        <div className="op-detail">
          <span>{'Désignation : '}</span>
          <span>{offerer.name}</span>
        </div>
        <div className="op-detail">
          <span>{'Siège social : '}</span>
          <span>
            {`${offerer.address} - ${offerer.postalCode} ${offerer.city}`}
          </span>
        </div>
      </div>
      {offerer.areBankInformationProvided && (
        <BankInformation
          hasBusinessUnitError={hasInvalidBusinessUnits}
          offerer={offerer}
        />
      )}
      <ApiKey
        maxAllowedApiKeys={offerer.apiKey.maxAllowed}
        offererId={offerer.id}
        reloadOfferer={loadOfferer}
        savedApiKeys={offerer.apiKey.savedApiKeys}
      />
      <VenuesContainer offererId={offerer.id} venues={physicalVenues} />
    </div>
  )
}

OffererDetails.propTypes = {
  offererId: PropTypes.string.isRequired,
}

export default OffererDetails
