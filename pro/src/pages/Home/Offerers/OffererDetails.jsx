import PropTypes from 'prop-types'
import React, { useEffect, useMemo, useState } from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import FullExternalSite from 'icons/full-external-site.svg'
import { ReactComponent as ClosedEyeSvg } from 'icons/ico-eye-full-close.svg'
import { ReactComponent as OpenedEyeSvg } from 'icons/ico-eye-full-open.svg'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'
import { Banner, Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Select from 'ui-kit/form_raw/Select'

import { STEP_OFFERER_HASH } from '../HomepageBreadcrumb'

import MissingReimbursementPoints from './MissingReimbursementPoints/MissingReimbursementPoints'
import VenueCreationLinks from './VenueCreationLinks'

const OffererDetails = ({
  handleChangeOfferer,
  isUserOffererValidated,
  offererOptions,
  selectedOfferer,
}) => {
  const newOfferCreation = useNewOfferCreationJourney()
  const { logEvent } = useAnalytics()

  const hasAtLeastOnePhysicalVenue = selectedOfferer.managedVenues
    .filter(venue => !venue.isVirtual)
    .map(venue => venue.id)
    .some(Boolean)

  const hasAtLeastOneVirtualVenue = selectedOfferer.managedVenues
    .filter(venue => venue.isVirtual)
    .map(venue => venue.id)
    .some(Boolean)

  const hasMissingReimbursementPoints = useMemo(() => {
    if (!selectedOfferer) {
      return false
    }
    return selectedOfferer.managedVenues
      .filter(venue => !venue.isVirtual)
      .map(venue => venue.hasMissingReimbursementPoint)
      .some(Boolean)
  }, [selectedOfferer])

  const showCreateVenueBanner =
    selectedOfferer.isValidated &&
    isUserOffererValidated &&
    !hasAtLeastOnePhysicalVenue

  const showMissingReimbursmentPointsBanner =
    selectedOfferer.isValidated && hasMissingReimbursementPoints

  const showOffererNotValidatedAndNoPhysicalVenue =
    !selectedOfferer.isValidated &&
    isUserOffererValidated &&
    !hasAtLeastOnePhysicalVenue

  const showOffererNotValidatedAndPhysicalVenue =
    !selectedOfferer.isValidated &&
    isUserOffererValidated &&
    hasAtLeastOnePhysicalVenue

  const refreshIsExpanded = () => {
    return (
      hasMissingReimbursementPoints ||
      !isUserOffererValidated ||
      showCreateVenueBanner ||
      showMissingReimbursmentPointsBanner ||
      showOffererNotValidatedAndNoPhysicalVenue ||
      showOffererNotValidatedAndPhysicalVenue
    )
  }

  const [isExpanded, setIsExpanded] = useState(refreshIsExpanded())

  useEffect(
    () => setIsExpanded(refreshIsExpanded()),
    [
      isUserOffererValidated,
      selectedOfferer.isValidated,
      hasAtLeastOnePhysicalVenue,
      hasMissingReimbursementPoints,
    ]
  )

  const toggleVisibility = () => {
    logEvent?.(Events.CLICKED_TOGGLE_HIDE_OFFERER_NAME, {
      isExpanded: isExpanded,
    })
    setIsExpanded(currentVisibility => !currentVisibility)
  }

  return (
    <div className="h-card h-card-secondary" data-testid="offerrer-wrapper">
      <div
        className={`h-card-inner${
          isExpanded && !newOfferCreation ? '' : ' h-no-bottom'
        }`}
      >
        <div
          className={`${!newOfferCreation ? 'od-header' : 'od-header-large'}`}
        >
          <Select
            handleSelection={handleChangeOfferer}
            id={STEP_OFFERER_HASH}
            label=""
            name="offererId"
            options={offererOptions}
            selectedValue={selectedOfferer.nonHumanizedId.toString()}
          />
          <div className="od-separator vertical" />
          {!newOfferCreation && (
            <>
              <Button
                className={isExpanded ? ' od-primary' : ''}
                variant={ButtonVariant.TERNARY}
                Icon={isExpanded ? ClosedEyeSvg : OpenedEyeSvg}
                onClick={toggleVisibility}
                type="button"
              >
                {isExpanded ? 'Masquer' : 'Afficher'}
              </Button>

              <div className="od-separator vertical small" />
            </>
          )}
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `/structures/${selectedOfferer.nonHumanizedId}`,
              isExternal: false,
            }}
            Icon={PenIcon}
            isDisabled={!isUserOffererValidated}
            onClick={() =>
              logEvent?.(Events.CLICKED_MODIFY_OFFERER, {
                offerer_id: selectedOfferer.id,
              })
            }
          >
            Modifier
          </ButtonLink>
        </div>

        {isExpanded && (
          <>
            <div className="od-separator horizontal" />
            {!isUserOffererValidated && (
              <Banner
                type="notification-info"
                className="banner"
                links={[
                  {
                    href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
                    linkTitle: 'En savoir plus',
                    Icon: FullExternalSite,
                  },
                ]}
              >
                <strong>
                  Le rattachement à votre structure est en cours de traitement
                  par les équipes du pass Culture
                </strong>
                <br />
                Un email vous sera envoyé lors de la validation de votre
                rattachement. Vous aurez alors accès à l’ensemble des
                fonctionnalités du pass Culture Pro.
              </Banner>
            )}
            {showOffererNotValidatedAndPhysicalVenue && (
              <Banner
                type="notification-info"
                className="banner"
                links={[
                  {
                    href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
                    linkTitle:
                      'En savoir plus sur le fonctionnement du pass Culture',
                    Icon: FullExternalSite,
                  },
                ]}
              >
                <strong>
                  Votre structure est en cours de traitement par les équipes du
                  pass Culture
                </strong>
                <br />
                Toutes les offres créées à l’échelle de vos lieux seront
                publiées sous réserve de validation de votre structure.
              </Banner>
            )}
            {showOffererNotValidatedAndNoPhysicalVenue && (
              <Banner
                type="notification-info"
                className="banner"
                links={[
                  {
                    href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
                    linkTitle: 'En savoir plus',
                    Icon: FullExternalSite,
                  },
                ]}
              >
                <strong>
                  Votre structure est en cours de traitement par les équipes du
                  pass Culture
                </strong>
                <br />
                Nous vous invitons à créer un lieu afin de pouvoir proposer des
                offres physiques ou des évènements. Vous pouvez dès à présent
                créer des offres numériques.
                <br />
                L’ensemble de ces offres seront publiées sous réserve de
                validation de votre structure.
              </Banner>
            )}

            {selectedOfferer.isValidated && !newOfferCreation && (
              <div className="h-card-cols">
                <div className="h-card-col">
                  <h3 className="h-card-secondary-title">
                    Informations pratiques
                  </h3>
                  <div className="h-card-content">
                    <ul className="h-description-list">
                      <li className="h-dl-row">
                        <span className="h-dl-title">Siren :</span>
                        <span className="h-dl-description">
                          {selectedOfferer.siren}
                        </span>
                      </li>

                      <li className="h-dl-row">
                        <span className="h-dl-title">Désignation :</span>
                        <span className="h-dl-description">
                          {selectedOfferer.name}
                        </span>
                      </li>

                      <li className="h-dl-row">
                        <span className="h-dl-title">{'Siège social : '}</span>
                        <address className="od-address">
                          {`${selectedOfferer.address} `}
                          {showMissingReimbursmentPointsBanner && <br />}
                          {`${selectedOfferer.postalCode} ${selectedOfferer.city}`}
                        </address>
                      </li>
                    </ul>
                  </div>
                </div>

                {showMissingReimbursmentPointsBanner && (
                  <div className="h-card-col">
                    <MissingReimbursementPoints />
                  </div>
                )}
              </div>
            )}
            {showCreateVenueBanner && (
              <Banner
                type="notification-info"
                className="banner"
                links={[
                  {
                    href: `https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-`,
                    linkTitle: 'En savoir plus sur la création d’un lieu',
                    Icon: FullExternalSite,
                  },
                ]}
              >
                <p>
                  Nous vous invitons à créer un lieu, cela vous permettra
                  ensuite de créer des offres physiques ou des évènements qui
                  seront réservables.
                </p>
                <br />
                <p>
                  Vous avez la possibilité de créer dès maintenant des offres
                  numériques.
                </p>
              </Banner>
            )}
            {isUserOffererValidated &&
              !hasAtLeastOnePhysicalVenue &&
              !newOfferCreation && (
                <VenueCreationLinks
                  hasPhysicalVenue={hasAtLeastOnePhysicalVenue}
                  hasVirtualOffers={hasAtLeastOneVirtualVenue}
                  offererId={selectedOfferer.nonHumanizedId}
                />
              )}
          </>
        )}
      </div>
    </div>
  )
}

OffererDetails.propTypes = {
  handleChangeOfferer: PropTypes.func.isRequired,
  isUserOffererValidated: PropTypes.bool.isRequired,
  offererOptions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      displayName: PropTypes.string.isRequired,
    })
  ).isRequired,
  selectedOfferer: PropTypes.shape().isRequired,
}

export default OffererDetails
