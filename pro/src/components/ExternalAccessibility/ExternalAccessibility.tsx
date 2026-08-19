import type { GetVenueResponseModel } from '@/apiClient/v1'
import { AccessibilityCallout } from '@/components/VenueEdition/AccessibilityCallout/AccessibilityCallout'
import strokeAccessibilityBrainIcon from '@/icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from '@/icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from '@/icons/stroke-accessibility-leg.svg'

import styles from './ExternalAccessibility.module.scss'
import { ExternalAccessibilityCollapse } from './ExternalAccessibilityCollapse/ExternalAccessibilityCollapse'

interface ExternalAccessibilityProps {
  externalAccessibilityId: GetVenueResponseModel['externalAccessibilityId']
  externalAccessibilityData: NonNullable<
    GetVenueResponseModel['externalAccessibilityData']
  >
}

export const ExternalAccessibility = ({
  externalAccessibilityId,
  externalAccessibilityData,
}: ExternalAccessibilityProps) => {
  return (
    <>
      <div className={styles['sections-container']}>
        <ExternalAccessibilityCollapse
          title="Handicap moteur"
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleMotorDisability
          )}
          icon={strokeAccessibilityLegIcon}
        >
          <ul className={styles['details']}>
            <li>
              <p className={styles['details-label']}>Stationnement</p>
              <p className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.parking ??
                  'Non renseigné'}
              </p>
            </li>
            <li>
              <p className={styles['details-label']}>Accès exterieur</p>
              <p className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.exterior ??
                  'Non renseigné'}
              </p>
            </li>
            <li>
              <p className={styles['details-label']}>Entrée du bâtiment</p>
              <p className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.entrance ??
                  'Non renseigné'}
              </p>
            </li>
            <li>
              <p className={styles['details-label']}>Sanitaire</p>
              <p className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.facilities ??
                  'Non renseigné'}
              </p>
            </li>
          </ul>
        </ExternalAccessibilityCollapse>
        <ExternalAccessibilityCollapse
          title="Handicap cognitif"
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleMentalDisability
          )}
          icon={strokeAccessibilityBrainIcon}
        >
          <div className={styles['details']}>
            <div>
              <p className={styles['details-label']}>Personnel</p>
              <p className={styles['details-item']}>
                {externalAccessibilityData.mentalDisability?.trainedPersonnel ??
                  'Non renseigné'}
              </p>
            </div>
          </div>
        </ExternalAccessibilityCollapse>
        <ExternalAccessibilityCollapse
          title="Handicap auditif"
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleAudioDisability
          )}
          icon={strokeAccessibilityEarIcon}
        >
          <div className={styles['details']}>
            <div>
              <p className={styles['details-label']}>
                Équipement sourd & malentendant
              </p>
              <div className={styles['details-item']}>
                {externalAccessibilityData.audioDisability?.deafAndHardOfHearing
                  ?.length ? (
                  <ul className={styles['details-list']}>
                    {externalAccessibilityData.audioDisability.deafAndHardOfHearing.map(
                      (item) => (
                        <li key={item}>{item}</li>
                      )
                    )}
                  </ul>
                ) : (
                  <p className={styles['details-item-text']}>Non renseigné</p>
                )}
              </div>
            </div>
          </div>
        </ExternalAccessibilityCollapse>
        <ExternalAccessibilityCollapse
          title="Handicap visuel"
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleVisualDisability
          )}
          icon={strokeAccessibilityEyeIcon}
        >
          <ul className={styles['details']}>
            <li>
              <p className={styles['details-label']}>Audiodescription</p>
              <div className={styles['details-item']}>
                {externalAccessibilityData.visualDisability?.audioDescription
                  ?.length ? (
                  <ul className={styles['details-list']}>
                    {externalAccessibilityData.visualDisability.audioDescription.map(
                      (item) => (
                        <li key={item}>{item}</li>
                      )
                    )}
                  </ul>
                ) : (
                  <p className={styles['details-item-text']}>Non renseigné</p>
                )}
              </div>
            </li>
            <li>
              <p className={styles['details-label']}>Balise sonore</p>
              <p className={styles['details-item']}>
                {externalAccessibilityData.visualDisability?.soundBeacon ??
                  'Non renseigné'}
              </p>
            </li>
          </ul>
        </ExternalAccessibilityCollapse>
      </div>
      <AccessibilityCallout
        className={styles['callout']}
        externalAccessibilityId={externalAccessibilityId}
      />
    </>
  )
}
