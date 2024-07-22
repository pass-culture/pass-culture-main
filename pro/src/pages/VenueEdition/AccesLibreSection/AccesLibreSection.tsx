import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import fullLinkIcon from 'icons/full-link.svg'
import strokeAccessibilityBrain from 'icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEar from 'icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEye from 'icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLeg from 'icons/stroke-accessibility-leg.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { AccesLibreCollapse } from './AccesLibreCollapse'
import styles from './AccesLibreSection.module.scss'

export interface AccesLibreSectionProps {
  venue: GetVenueResponseModel
}

export const AccesLibreSection = ({ venue }: AccesLibreSectionProps) => {
  if (!venue.externalAccessibilityData) {
    return
  }

  return (
    <SummarySection
      title="Modalités d’accessibilité via acceslibre"
      editLink={
        <ButtonLink
          to={`https://acceslibre.beta.gouv.fr/contrib/edit-infos/${venue.externalAccessibilityId}/`}
          isExternal
          icon={fullLinkIcon}
        >
          Éditer sur acceslibre
        </ButtonLink>
      }
    >
      <p>
        Les modalités ci-dessous sont issues de la plateforme{' '}
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          isExternal
          to={
            venue.externalAccessibilityUrl ?? 'https://acceslibre.beta.gouv.fr/'
          }
        >
          acceslibre.gouv.fr
        </ButtonLink>
        . Vous pouvez les modifier directement depuis cette plateforme.
      </p>

      <div className={styles['sections-container']}>
        <div className={styles['sections-column']}>
          <AccesLibreCollapse
            title="Handicap moteur"
            isAccessible={Boolean(
              venue.externalAccessibilityData.isAccessibleMotorDisability
            )}
            icon={strokeAccessibilityLeg}
          >
            <ul className={styles['details']}>
              <li>
                <span className={styles['details-label']}>Stationnement</span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.motorDisability?.parking ??
                    'Non renseigné'}
                </span>
              </li>
              <li>
                <span className={styles['details-label']}>Accès exterieur</span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.motorDisability?.exterior ??
                    'Non renseigné'}
                </span>
              </li>
              <li>
                <span className={styles['details-label']}>
                  Entrée du bâtiment
                </span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.motorDisability?.entrance ??
                    'Non renseigné'}
                </span>
              </li>
              <li>
                <span className={styles['details-label']}>Sanitaire</span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.motorDisability
                    ?.facilities ?? 'Non renseigné'}
                </span>
              </li>
            </ul>
          </AccesLibreCollapse>

          <AccesLibreCollapse
            title="Handicap cognitif"
            isAccessible={Boolean(
              venue.externalAccessibilityData.isAccessibleMentalDisability
            )}
            icon={strokeAccessibilityBrain}
          >
            <div className={styles['details']}>
              <div>
                <span className={styles['details-label']}>Personnel</span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.mentalDisability
                    ?.trainedPersonnel ?? 'Non renseigné'}
                </span>
              </div>
            </div>
          </AccesLibreCollapse>
        </div>

        <div className={styles['sections-column']}>
          <AccesLibreCollapse
            title="Handicap auditif"
            isAccessible={Boolean(
              venue.externalAccessibilityData.isAccessibleAudioDisability
            )}
            icon={strokeAccessibilityEar}
          >
            <div className={styles['details']}>
              <div>
                <span className={styles['details-label']}>
                  Équipement sourd & malentendant
                </span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.audioDisability
                    ?.deafAndHardOfHearing?.length ? (
                    <ul className={styles['details-list']}>
                      {venue.externalAccessibilityData.audioDisability.deafAndHardOfHearing.map(
                        (item) => (
                          <li key={item}>{item}</li>
                        )
                      )}
                    </ul>
                  ) : (
                    'Non renseigné'
                  )}
                </span>
              </div>
            </div>
          </AccesLibreCollapse>

          <AccesLibreCollapse
            title="Handicap visuel"
            isAccessible={Boolean(
              venue.externalAccessibilityData.isAccessibleVisualDisability
            )}
            icon={strokeAccessibilityEye}
          >
            <ul className={styles['details']}>
              <li>
                <span className={styles['details-label']}>
                  Audiodescription
                </span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.visualDisability
                    ?.audioDescription?.length ? (
                    <ul className={styles['details-list']}>
                      {venue.externalAccessibilityData.visualDisability.audioDescription.map(
                        (item) => (
                          <li key={item}>{item}</li>
                        )
                      )}
                    </ul>
                  ) : (
                    'Non renseigné'
                  )}
                </span>
              </li>
              <li>
                <span className={styles['details-label']}>Balise sonore</span>
                <span className={styles['details-item']}>
                  {venue.externalAccessibilityData.visualDisability
                    ?.soundBeacon ?? 'Non renseigné'}
                </span>
              </li>
            </ul>
          </AccesLibreCollapse>
        </div>
      </div>
    </SummarySection>
  )
}
