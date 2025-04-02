import { GetVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import strokeAccessibilityBrainIcon from 'icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from 'icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from 'icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from 'icons/stroke-accessibility-leg.svg'
import { AccessibilityCallout } from 'pages/VenueEdition/AccessibilityCallout/AccessibilityCallout'

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
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')

  return (
    <>
      <div className={styles['sections-container']}>
        <ExternalAccessibilityCollapse
          title="Handicap moteur"
          titleHeadingLevel={isOpenToPublicEnabled ? 'h5' : 'h4'}
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleMotorDisability
          )}
          icon={strokeAccessibilityLegIcon}
        >
          <ul className={styles['details']}>
            <li>
              <span className={styles['details-label']}>Stationnement</span>
              <span className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.parking ??
                  'Non renseigné'}
              </span>
            </li>
            <li>
              <span className={styles['details-label']}>Accès exterieur</span>
              <span className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.exterior ??
                  'Non renseigné'}
              </span>
            </li>
            <li>
              <span className={styles['details-label']}>
                Entrée du bâtiment
              </span>
              <span className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.entrance ??
                  'Non renseigné'}
              </span>
            </li>
            <li>
              <span className={styles['details-label']}>Sanitaire</span>
              <span className={styles['details-item']}>
                {externalAccessibilityData.motorDisability?.facilities ??
                  'Non renseigné'}
              </span>
            </li>
          </ul>
        </ExternalAccessibilityCollapse>
        <ExternalAccessibilityCollapse
          title="Handicap cognitif"
          titleHeadingLevel={isOpenToPublicEnabled ? 'h5' : 'h4'}
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleMentalDisability
          )}
          icon={strokeAccessibilityBrainIcon}
        >
          <div className={styles['details']}>
            <div>
              <span className={styles['details-label']}>Personnel</span>
              <span className={styles['details-item']}>
                {externalAccessibilityData.mentalDisability?.trainedPersonnel ??
                  'Non renseigné'}
              </span>
            </div>
          </div>
        </ExternalAccessibilityCollapse>
        <ExternalAccessibilityCollapse
          title="Handicap auditif"
          titleHeadingLevel={isOpenToPublicEnabled ? 'h5' : 'h4'}
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleAudioDisability
          )}
          icon={strokeAccessibilityEarIcon}
        >
          <div className={styles['details']}>
            <div>
              <span className={styles['details-label']}>
                Équipement sourd & malentendant
              </span>
              <span className={styles['details-item']}>
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
                  'Non renseigné'
                )}
              </span>
            </div>
          </div>
        </ExternalAccessibilityCollapse>
        <ExternalAccessibilityCollapse
          title="Handicap visuel"
          titleHeadingLevel={isOpenToPublicEnabled ? 'h5' : 'h4'}
          isAccessible={Boolean(
            externalAccessibilityData.isAccessibleVisualDisability
          )}
          icon={strokeAccessibilityEyeIcon}
        >
          <ul className={styles['details']}>
            <li>
              <span className={styles['details-label']}>Audiodescription</span>
              <span className={styles['details-item']}>
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
                  'Non renseigné'
                )}
              </span>
            </li>
            <li>
              <span className={styles['details-label']}>Balise sonore</span>
              <span className={styles['details-item']}>
                {externalAccessibilityData.visualDisability?.soundBeacon ??
                  'Non renseigné'}
              </span>
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
