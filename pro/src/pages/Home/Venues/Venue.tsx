import cn from 'classnames'
import { addDays, isBefore } from 'date-fns'
import React, { useState } from 'react'

import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { VenueEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullDisclosureClose from 'icons/full-disclosure-close.svg'
import fullDisclosureOpen from 'icons/full-disclosure-open.svg'
import fullEditIcon from 'icons/full-edit.svg'
import fullErrorIcon from 'icons/full-error.svg'
import fullMoreIcon from 'icons/full-more.svg'
import strokeConnectIcon from 'icons/stroke-connect.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { VenueOfferSteps } from '../VenueOfferSteps'

import styles from './Venue.module.scss'

export interface VenueProps {
  hasMissingReimbursementPoint?: boolean
  venueId: number
  isVirtual?: boolean
  name: string
  offererId: number
  publicName?: string | null
  offererHasCreatedOffer?: boolean
  venueHasCreatedOffer?: boolean
  hasProvider?: boolean
  dmsInformations?: DMSApplicationForEAC | null
  hasAdageId?: boolean
  adageInscriptionDate?: string | null
  hasPendingBankInformationApplication?: boolean | null
  demarchesSimplifieesApplicationId?: number | null
  offererHasBankAccount: boolean
  hasNonFreeOffer: boolean
  isFirstVenue: boolean
}

const Venue = ({
  hasMissingReimbursementPoint = false,
  venueId,
  isVirtual = false,
  name,
  offererId,
  hasProvider,
  publicName,
  offererHasCreatedOffer,
  venueHasCreatedOffer,
  dmsInformations,
  hasAdageId,
  adageInscriptionDate,
  demarchesSimplifieesApplicationId,
  hasPendingBankInformationApplication = false,
  offererHasBankAccount,
  hasNonFreeOffer,
  isFirstVenue,
}: VenueProps) => {
  const hasAdageIdForMoreThan30Days =
    hasAdageId &&
    !!adageInscriptionDate &&
    isBefore(new Date(adageInscriptionDate), addDays(new Date(), -30))

  const hasRefusedApplicationForMoreThan30Days =
    (dmsInformations?.state == DMSApplicationstatus.REFUSE ||
      dmsInformations?.state == DMSApplicationstatus.SANS_SUITE) &&
    dmsInformations.processingDate &&
    isBefore(
      new Date(dmsInformations?.processingDate),
      addDays(new Date(), -30)
    )

  const shouldDisplayEACInformationSection =
    Boolean(dmsInformations) &&
    !hasAdageIdForMoreThan30Days &&
    !hasRefusedApplicationForMoreThan30Days

  const shouldShowVenueOfferSteps =
    shouldDisplayEACInformationSection ||
    !venueHasCreatedOffer ||
    hasPendingBankInformationApplication

  const [prevInitialOpenState, setPrevInitialOpenState] = useState(
    shouldShowVenueOfferSteps
  )
  const [prevOffererId, setPrevOffererId] = useState(offererId)
  const [isToggleOpen, setIsToggleOpen] = useState(shouldShowVenueOfferSteps)
  const { logEvent } = useAnalytics()
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const venueIdTrackParam = {
    venue_id: venueId,
  }

  if (prevInitialOpenState != shouldShowVenueOfferSteps) {
    setIsToggleOpen(shouldShowVenueOfferSteps)
    setPrevInitialOpenState(shouldShowVenueOfferSteps)
  }

  if (offererId !== prevOffererId) {
    setPrevOffererId(offererId)
  }

  const editVenueLink = `/structures/${offererId}/lieux/${venueId}?modification`
  const reimbursementSectionLink = `/structures/${offererId}/lieux/${venueId}?modification#remboursement`

  return (
    <div
      className="h-section-row nested offerer-venue"
      data-testid="venue-wrapper"
    >
      <div
        className={cn(
          `h-card`,
          { 'h-card-primary': isVirtual },
          { 'h-card-secondary': !isVirtual }
        )}
      >
        <div className="h-card-inner">
          <div
            className={cn('h-card-header-row', {
              'h-card-is-open': isToggleOpen,
            })}
          >
            <h3 className="h-card-title">
              {shouldShowVenueOfferSteps ? (
                <button
                  className={cn('h-card-title', styles['toggle-wrapper'])}
                  type="button"
                  onClick={() => {
                    setIsToggleOpen((prev) => !prev)
                    logEvent?.(
                      VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                      venueIdTrackParam
                    )
                  }}
                >
                  <SvgIcon
                    alt={`${
                      isToggleOpen ? 'Masquer' : 'Afficher'
                    } les statistiques`}
                    className={styles['toggle-icon']}
                    viewBox="0 0 16 16"
                    src={
                      isToggleOpen ? fullDisclosureOpen : fullDisclosureClose
                    }
                  />
                  <span>{publicName || name}</span>
                </button>
              ) : (
                <div className={cn('h-card-title', styles['toggle-wrapper'])}>
                  {publicName || name}
                </div>
              )}

              {true && (
                <Button
                  icon={fullErrorIcon}
                  className="needs-payment-icon"
                  variant={ButtonVariant.TERNARY}
                  hasTooltip
                  onClick={() => {
                    setIsToggleOpen((prev) => !prev)
                    logEvent?.(
                      VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                      venueIdTrackParam
                    )
                  }}
                >
                  Cliquer pour voir les prochaines étapes
                </Button>
              )}

              {hasProvider && (
                <Tag
                  variant={TagVariant.LIGHT_PURPLE}
                  className={styles['api-tag']}
                >
                  <SvgIcon alt="" src={strokeConnectIcon} />
                  API
                </Tag>
              )}
            </h3>

            <div className="button-group">
              {/*Delete when WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is deleted*/}
              {!isNewBankDetailsJourneyEnabled &&
                hasMissingReimbursementPoint &&
                !isVirtual &&
                venueHasCreatedOffer && (
                  <>
                    <ButtonLink
                      variant={ButtonVariant.TERNARYPINK}
                      link={{
                        to: reimbursementSectionLink,
                        isExternal: false,
                      }}
                      onClick={() => {
                        logEvent?.(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
                          from: location.pathname,
                          ...venueIdTrackParam,
                        })
                      }}
                      icon={fullMoreIcon}
                    >
                      Ajouter un RIB
                    </ButtonLink>
                    <span className="button-group-separator" />
                  </>
                )}
              <ButtonLink
                variant={ButtonVariant.TERNARY}
                link={{
                  to: editVenueLink,
                  isExternal: false,
                }}
                icon={fullEditIcon}
                onClick={() =>
                  logEvent?.(
                    VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
                    venueIdTrackParam
                  )
                }
              >
                Éditer le lieu
              </ButtonLink>
            </div>
          </div>

          {isToggleOpen && shouldShowVenueOfferSteps && (
            <VenueOfferSteps
              venueId={venueId}
              hasVenue={true}
              offererId={offererId}
              venueHasCreatedOffer={venueHasCreatedOffer}
              offererHasCreatedOffer={offererHasCreatedOffer}
              hasMissingReimbursementPoint={hasMissingReimbursementPoint}
              hasAdageId={hasAdageId}
              shouldDisplayEACInformationSection={
                shouldDisplayEACInformationSection
              }
              hasPendingBankInformationApplication={
                hasPendingBankInformationApplication
              }
              demarchesSimplifieesApplicationId={
                demarchesSimplifieesApplicationId
              }
              offererHasBankAccount={offererHasBankAccount}
              hasNonFreeOffer={hasNonFreeOffer}
              isFirstVenue={isFirstVenue}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default Venue
