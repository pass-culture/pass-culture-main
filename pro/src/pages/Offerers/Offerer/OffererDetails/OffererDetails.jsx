import cn from 'classnames'
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
import styles from './OffererDetails.module.scss'
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
    return <Spinner />
  }

  return offerer ? (
    <div className={styles['offerer-page']}>
      <ButtonLink
        link={{ to: `/accueil?structure=${offerer.id}`, isExternal: false }}
        variant={ButtonVariant.QUATERNARY}
        Icon={CircleArrowIcon}
        className={styles['offerer-page-go-back-link']}
      >
        Accueil
      </ButtonLink>
      <PageTitle title="Détails de votre structure" />
      <Titles subtitle={offerer.name} title="Structure" />
      <p className={styles['op-teaser']}>
        Détails de la structure rattachée, des lieux et des fournisseurs de ses
        offres.
      </p>
      <div className={cn(styles['section'], styles['op-content-section'])}>
        <h2 className={styles['main-list-title']}>Informations structure</h2>
        <div className={styles['op-detail']}>
          <span>{'SIREN : '}</span>
          <span>{offerer.formattedSiren}</span>
        </div>
        <div className={styles['op-detail']}>
          <span>{'Désignation : '}</span>
          <span>{offerer.name}</span>
        </div>
        <div className={styles['op-detail']}>
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
      <Venues offererId={offerer.nonHumanizedId} venues={physicalVenues} />
    </div>
  ) : (
    <></>
  )
}

export default OffererDetails
