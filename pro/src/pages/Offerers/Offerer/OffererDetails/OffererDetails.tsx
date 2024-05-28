import React, { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import fullBackIcon from 'icons/full-back.svg'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { hasProperty } from 'utils/types'

import ApiKey from './ApiKey/ApiKey'
import AttachmentInvitations from './AttachmentInvitations/AttachmentInvitations'
import {
  formatSiren,
  Offerer,
  transformOffererResponseModelToOfferer,
} from './Offerer'
import styles from './OffererDetails.module.scss'
import Venues from './Venues/Venues'

export const OffererDetails = () => {
  const { offererId } = useParams()
  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [physicalVenues, setPhysicalVenues] = useState<
    GetOffererVenueResponseModel[]
  >([])
  const [isLoading, setIsLoading] = useState(true)

  const resetOfferer = useCallback(() => {
    setOfferer(null)
    setPhysicalVenues([])
  }, [])

  const loadOfferer = useCallback(
    async (id: number) => {
      try {
        const receivedOfferer = await api.getOfferer(id)
        setOfferer(transformOffererResponseModelToOfferer(receivedOfferer))
        setPhysicalVenues(
          receivedOfferer.managedVenues?.filter((venue) => !venue.isVirtual) ??
            []
        )
      } catch (error) {
        // TODO should redirect to a 404 page instead
        if (
          hasProperty(error, 'status') &&
          error.status === HTTP_STATUS.FORBIDDEN
        ) {
          resetOfferer()
        }
      }
    },
    [resetOfferer]
  )

  useEffect(() => {
    async function initializeOfferer(id: number) {
      try {
        await loadOfferer(id)
      } catch (error) {
        // TODO should redirect to a 404 page instead
        if (
          hasProperty(error, 'status') &&
          error.status === HTTP_STATUS.FORBIDDEN
        ) {
          resetOfferer()
        }
      }
      setIsLoading(false)
    }

    if (offererId) {
      void initializeOfferer(Number(offererId))
    }
  }, [offererId, loadOfferer, resetOfferer])

  if (isLoading) {
    return <Spinner />
  }

  return (
    <AppLayout>
      {offerer ? (
        <div className={styles['offerer-page']}>
          <ButtonLink
            link={{
              to: `/accueil?structure=${offerer.id}`,
              isExternal: false,
            }}
            variant={ButtonVariant.TERNARY}
            icon={fullBackIcon}
            className={styles['offerer-page-go-back-link']}
          >
            Accueil
          </ButtonLink>

          <div className={styles['offerer-form-heading']}>
            <div className={styles['title-page']}>
              <h1>Structure</h1>
            </div>
            <h2 className={styles['offerer-name']}>{offerer.name}</h2>
            <div className={styles['description']}>
              Détails de la structure rattachée, des collaborateurs, des lieux
              et des fournisseurs de ses offres
            </div>
          </div>

          <div className={styles['offerer-page-container']}>
            <div className={styles['section']}>
              <h2 className={styles['main-list-title']}>
                Informations structure
              </h2>
              <div className={styles['op-detail']}>
                <span>{'SIREN : '}</span>
                <span>{formatSiren(offerer.siren)}</span>
              </div>
              <div className={styles['op-detail']}>
                <span>{'Désignation : '}</span>
                <span>{offerer.name}</span>
              </div>
              <div className={styles['op-detail']}>
                <span>{'Siège social : '}</span>
                <span>
                  {`${offerer.street} - ${offerer.postalCode} ${offerer.city}`}
                </span>
              </div>
            </div>

            <AttachmentInvitations offererId={offerer.id} />

            <ApiKey
              maxAllowedApiKeys={offerer.apiKey.maxAllowed}
              offererId={offerer.id}
              reloadOfferer={loadOfferer}
              savedApiKeys={offerer.apiKey.savedApiKeys}
            />

            <Venues offererId={offerer.id} venues={physicalVenues} />
          </div>
        </div>
      ) : (
        <></>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OffererDetails
