import React, { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import PageTitle from 'components/PageTitle/PageTitle'
import { ReactComponent as CircleArrowIcon } from 'icons/ico-circle-arrow-left.svg'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import Titles from 'ui-kit/Titles/Titles'

import ApiKey from './ApiKey/ApiKey'
import { Offerer } from './Offerer'
import Venues from './Venues/Venues'

const OffererDetails = () => {
  const { offererId } = useParams()
  const [offerer, setOfferer] = useState(null)
  const [physicalVenues, setPhysicalVenues] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const resetOfferer = useCallback(id => {
    setOfferer({ id: id, managedVenues: [] })
    setPhysicalVenues([])
  }, [])

  const loadOfferer = useCallback(
    async id => {
      try {
        const receivedOfferer = await api.getOfferer(id)
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

  return offerer ? (
    <div className="offerer-page">
      <ButtonLink
        link={{ to: `/accueil?structure=${offerer.id}`, isExternal: false }}
        variant={ButtonVariant.QUATERNARY}
        Icon={CircleArrowIcon}
        className="offerer-page-go-back-link"
      >
        Accueil
      </ButtonLink>
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
      <ApiKey
        maxAllowedApiKeys={offerer.apiKey.maxAllowed}
        offererId={offerer.nonHumanizedId}
        reloadOfferer={loadOfferer}
        savedApiKeys={offerer.apiKey.savedApiKeys}
      />
      <Venues offererId={offerer.id} venues={physicalVenues} />
    </div>
  ) : (
    <></>
  )
}

export default OffererDetails
