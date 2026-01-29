import cn from 'classnames'

import type {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  VenueEvents,
} from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Card } from '@/components/Card/Card'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullInfoIcon from '@/icons/full-info.svg'
import fullNextIcon from '@/icons/full-next.svg'

import {
  shouldDisplayEACInformationSectionForVenue,
  shouldShowVenueOfferStepsForVenue,
} from '../Offerers/components/VenueList/venueUtils'
import styles from './VenueOfferSteps.module.scss'

export interface VenueOfferStepsProps {
  offerer: GetOffererResponseModel
  venue?: GetOffererVenueResponseModel | GetVenueResponseModel
  hasVenue: boolean
  isFirstVenue?: boolean
  isInsidePartnerBlock?: boolean
  className?: string
}

export const VenueOfferSteps = ({
  offerer,
  venue,
  hasVenue = false,
  isFirstVenue = false,
  isInsidePartnerBlock = false,
  className,
}: VenueOfferStepsProps) => {
  const { logEvent } = useAnalytics()
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')

  const venueCreationUrl = isVenueCreationAvailable
    ? `/inscription/structure/recherche`
    : '/erreur/indisponible'

  const shouldShowVenueOfferSteps = shouldShowVenueOfferStepsForVenue(venue)

  if (!shouldShowVenueOfferSteps) {
    return null
  }

  const displayCreateStructureButton = !hasVenue

  const offererHasCreatedOffer = Boolean(
    offerer.managedVenues?.some((venue) => venue.hasCreatedOffer)
  )
  const offererHasBankAccount = Boolean(
    offerer.hasPendingBankAccount || offerer.hasValidBankAccount
  )

  /* Condition linked to add bank account banner
    display button if this is the first venue and the offerer has no offer at all,
    or if the offerer has no paid offerer
  */
  const displayAddBankAccountButton =
    !offererHasBankAccount &&
    ((!isFirstVenue && !offerer.hasNonFreeOffer) ||
      (isFirstVenue && !offererHasCreatedOffer))
  const displayAddEACInfoButton =
    venue && shouldDisplayEACInformationSectionForVenue(venue)

  const displayNextStepsSection =
    displayCreateStructureButton ||
    displayAddBankAccountButton ||
    displayAddEACInfoButton

  return (
    (displayNextStepsSection || displayAddEACInfoButton) && (
      <Card
        className={cn(styles['card-wrapper'], className, {
          [styles['no-shadow']]: hasVenue || isInsidePartnerBlock,
          [styles['inside-partner-block']]: isInsidePartnerBlock,
        })}
        data-testid={hasVenue ? 'venue-offer-steps' : 'home-offer-steps'}
      >
        {displayNextStepsSection && (
          <>
            <h3 className={styles['card-title']}>Prochaines étapes : </h3>

            <div className={styles['venue-offer-steps']}>
              {displayCreateStructureButton && (
                <div className={styles['step-venue-creation']}>
                  <Button
                    as="a"
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.NEUTRAL}
                    iconPosition={IconPositionEnum.RIGHT}
                    icon={fullNextIcon}
                    to={venueCreationUrl}
                    onClick={() => {
                      logEvent(Events.CLICKED_CREATE_VENUE, {
                        from: location.pathname,
                        is_first_venue: true,
                      })
                    }}
                    label=" Créer une structure"
                  />

                  <Button
                    as="a"
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    to="https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-"
                    isExternal
                    opensInNewTab
                    icon={fullInfoIcon}
                    onClick={() => {
                      logEvent(Events.CLICKED_NO_VENUE, {
                        from: location.pathname,
                      })
                    }}
                    label="  Je ne dispose pas de structure propre, quel type de
                      structure créer ?"
                  />
                </div>
              )}

              {displayAddBankAccountButton && (
                <Button
                  as="a"
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  iconPosition={IconPositionEnum.LEFT}
                  icon={fullNextIcon}
                  to={`remboursements/informations-bancaires?structure=${offerer.id}`}
                  onClick={() => {
                    logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
                      venue_id: venue?.id ?? '',
                      from: OFFER_FORM_NAVIGATION_IN.HOME,
                    })
                  }}
                  label="Ajouter un compte bancaire"
                />
              )}
              {displayAddEACInfoButton && (
                <Button
                  as="a"
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  iconPosition={IconPositionEnum.RIGHT}
                  icon={fullNextIcon}
                  to={`/structures/${offerer.id}/lieux/${venue.id}/collectif`}
                  label="Renseigner mes informations à destination des enseignants"
                />
              )}
            </div>
          </>
        )}

        {displayAddEACInfoButton && (
          <>
            <h3 className={styles['card-title']}>Démarche en cours : </h3>

            <div className={styles['venue-offer-steps']}>
              <Button
                as="a"
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                iconPosition={IconPositionEnum.RIGHT}
                icon={fullNextIcon}
                to={`/structures/${offerer.id}/lieux/${venue.id}/collectif`}
                onClick={() => {
                  logEvent(Events.CLICKED_EAC_DMS_TIMELINE, {
                    from: location.pathname,
                  })
                }}
                label="Suivre ma demande de référencement ADAGE"
              />
            </div>
          </>
        )}
      </Card>
    )
  )
}
