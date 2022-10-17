import PropTypes from 'prop-types'
import React, { useEffect, useMemo, useState } from 'react'

import Icon from 'components/layout/Icon'
import Select from 'components/layout/inputs/Select'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as ExternalSiteIcon } from 'icons/ico-external-site-filled.svg'
import { ReactComponent as ClosedEyeSvg } from 'icons/ico-eye-full-close.svg'
import { ReactComponent as OpenedEyeSvg } from 'icons/ico-eye-full-open.svg'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'
import { Banner, ButtonLink, Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { STEP_OFFERER_HASH } from '../HomepageBreadcrumb'

import BankInformations from './BankInformations'
import InvalidBusinessUnits from './InvalidBusinessUnits'
import MissingBusinessUnits from './MissingBusinessUnits'
import MissingReimbursementPoints from './MissingReimbursementPoints/MissingReimbursementPoints'
import VenueCreationLinks from './VenueCreationLinks'

const hasRejectedOrDraftBankInformation = offerer =>
  Boolean(
    offerer.demarchesSimplifieesApplicationId && !offerer.iban && !offerer.bic
  )

const initialIsExpanded = (
  hasPhysicalVenues,
  isBankInformationWithSiretActive,
  isNewBankInformationActive,
  hasInvalidBusinessUnits,
  hasMissingReimbursementPoints,
  hasMissingBusinessUnits
) => {
  return (
    !hasPhysicalVenues ||
    (isBankInformationWithSiretActive &&
      (hasInvalidBusinessUnits || hasMissingBusinessUnits)) ||
    (isNewBankInformationActive && hasMissingReimbursementPoints)
  )
}

const OffererDetails = ({
  businessUnitList,
  handleChangeOfferer,
  hasPhysicalVenues,
  isUserOffererValidated,
  offererOptions,
  selectedOfferer,
}) => {
  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const isNewBankInformationActive = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )
  const { logEvent } = useAnalytics()

  const hasRejectedOrDraftOffererBankInformations = useMemo(() => {
    if (!selectedOfferer) return false
    return hasRejectedOrDraftBankInformation(selectedOfferer)
  }, [selectedOfferer])

  const hasInvalidBusinessUnits = useMemo(() => {
    if (!isBankInformationWithSiretActive) return false
    if (!selectedOfferer) return false
    return (
      businessUnitList.filter(businessUnit => !businessUnit.siret).length > 0
    )
  }, [selectedOfferer, businessUnitList, isBankInformationWithSiretActive])

  const hasMissingBusinessUnits = useMemo(() => {
    if (!isBankInformationWithSiretActive) return false
    if (!selectedOfferer) return false
    return selectedOfferer.managedVenues
      .filter(venue => !venue.isVirtual)
      .map(venue => !venue.businessUnitId)
      .some(Boolean)
  }, [isBankInformationWithSiretActive, selectedOfferer])

  const hasAtLeastOnePhysicalVenue = selectedOfferer.managedVenues
    .filter(venue => !venue.isVirtual)
    .map(venue => venue.id)
    .some(Boolean)

  const hasAtLeastOneVirtualVenue = selectedOfferer.managedVenues
    .filter(venue => venue.isVirtual)
    .map(venue => venue.id)
    .some(Boolean)

  const hasMissingReimbursementPoints = useMemo(() => {
    if (!isNewBankInformationActive) return false
    if (!selectedOfferer) return false
    return selectedOfferer.managedVenues
      .filter(venue => !venue.isVirtual)
      .map(venue => venue.hasMissingReimbursementPoint)
      .some(Boolean)
  }, [selectedOfferer, isNewBankInformationActive])

  const [isExpanded, setIsExpanded] = useState(
    initialIsExpanded(
      hasPhysicalVenues,
      isBankInformationWithSiretActive,
      isNewBankInformationActive,
      hasInvalidBusinessUnits,
      hasMissingReimbursementPoints,
      hasMissingBusinessUnits
    )
  )

  useEffect(
    () =>
      setIsExpanded(
        initialIsExpanded(
          hasPhysicalVenues,
          isBankInformationWithSiretActive,
          isNewBankInformationActive,
          hasInvalidBusinessUnits,
          hasMissingReimbursementPoints,
          hasMissingBusinessUnits
        )
      ),
    [
      hasPhysicalVenues,
      isBankInformationWithSiretActive,
      isNewBankInformationActive,
      hasInvalidBusinessUnits,
      hasMissingReimbursementPoints,
      hasMissingBusinessUnits,
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
      <div className={`h-card-inner${isExpanded ? '' : ' h-no-bottom'}`}>
        <div className="od-header">
          <Select
            handleSelection={handleChangeOfferer}
            id={STEP_OFFERER_HASH}
            label=""
            name="offererId"
            options={offererOptions}
            selectedValue={selectedOfferer.id}
          />
          <div className="od-separator vertical" />
          <Button
            className={isExpanded ? ' od-primary' : ''}
            variant={ButtonVariant.TERNARY}
            Icon={isExpanded ? ClosedEyeSvg : OpenedEyeSvg}
            onClick={toggleVisibility}
            type="button"
          >
            {isExpanded ? 'Masquer' : 'Afficher'}
          </Button>
          {isBankInformationWithSiretActive ? (
            hasInvalidBusinessUnits ? (
              <Icon
                alt="SIRET Manquant"
                className="ico-bank-warning"
                svg="ico-alert-filled"
              />
            ) : (
              hasMissingBusinessUnits && (
                <Icon
                  alt="Coordonnées bancaires manquantes"
                  className="ico-bank-warning"
                  svg="ico-alert-filled"
                />
              )
            )
          ) : (
            ((isNewBankInformationActive && hasMissingReimbursementPoints) ||
              (!isNewBankInformationActive &&
                selectedOfferer.hasMissingBankInformation)) && (
              <Icon
                alt="Informations bancaires manquantes"
                className="ico-bank-warning"
                svg="ico-alert-filled"
              />
            )
          )}
          <div className="od-separator vertical small" />
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `/structures/${selectedOfferer.id}`,
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
                    Icon: ExternalSiteIcon,
                  },
                ]}
              >
                <strong>
                  Le rattachement à votre structure est en cours de validation
                </strong>
                <br />
                Un e-mail vous sera envoyé lors de la validation de votre
                rattachement. Vous aurez alors accès à l’ensemble des
                fonctionnalités du pass Culture Pro.
              </Banner>
            )}
            {!selectedOfferer.isValidated &&
              isUserOffererValidated &&
              hasAtLeastOnePhysicalVenue && (
                <Banner
                  type="notification-info"
                  className="banner"
                  links={[
                    {
                      href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
                      linkTitle:
                        'En savoir plus sur le fonctionnement du pass Culture',
                      Icon: ExternalSiteIcon,
                    },
                  ]}
                >
                  <strong>Votre structure est en cours de validation</strong>
                  <br />
                  Toutes les offres créées à l’échelle de vos lieux seront
                  publiées sous réserve de validation de votre structure par nos
                  équipes.
                </Banner>
              )}
            {!selectedOfferer.isValidated &&
              isUserOffererValidated &&
              !hasAtLeastOnePhysicalVenue && (
                <Banner
                  type="notification-info"
                  className="banner"
                  links={[
                    {
                      href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
                      linkTitle: 'En savoir plus',
                      Icon: ExternalSiteIcon,
                    },
                  ]}
                >
                  <strong>Votre structure est en cours de validation</strong>
                  <br />
                  Nous vous invitons à créer un lieu afin de pouvoir proposer
                  des offres physiques ou des évènements. <br />
                  Vous pouvez dès à présent créer des offres numériques.
                  L’ensemble de ces offres sera publié une fois votre structure
                  validée.
                </Banner>
              )}

            {selectedOfferer.isValidated && (
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
                          {selectedOfferer.hasMissingBankInformation && <br />}
                          {`${selectedOfferer.postalCode} ${selectedOfferer.city}`}
                        </address>
                      </li>
                    </ul>
                  </div>
                </div>

                {isNewBankInformationActive && hasMissingReimbursementPoints && (
                  <div className="h-card-col">
                    <MissingReimbursementPoints />
                  </div>
                )}
                {isBankInformationWithSiretActive && (
                  <>
                    {hasInvalidBusinessUnits && (
                      <div className="h-card-col">
                        <InvalidBusinessUnits offererId={selectedOfferer.id} />
                      </div>
                    )}
                    {!hasInvalidBusinessUnits && hasMissingBusinessUnits && (
                      <div className="h-card-col">
                        <MissingBusinessUnits />
                      </div>
                    )}
                  </>
                )}
                {!isBankInformationWithSiretActive &&
                  !isNewBankInformationActive &&
                  (selectedOfferer.hasMissingBankInformation ||
                    hasRejectedOrDraftOffererBankInformations) && (
                    <div className="h-card-col">
                      <BankInformations
                        hasMissingBankInformation={
                          selectedOfferer.hasMissingBankInformation
                        }
                        hasRejectedOrDraftOffererBankInformations={
                          hasRejectedOrDraftOffererBankInformations
                        }
                        offerer={selectedOfferer}
                      />
                    </div>
                  )}
              </div>
            )}
            {selectedOfferer.isValidated &&
              isUserOffererValidated &&
              !hasAtLeastOnePhysicalVenue && (
                <Banner
                  type="notification-info"
                  className="banner"
                  links={[
                    {
                      href: `https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-`,
                      linkTitle: 'En savoir plus sur la création d’un lieu',
                      Icon: ExternalSiteIcon,
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
            {isUserOffererValidated && !hasAtLeastOnePhysicalVenue && (
              <VenueCreationLinks
                hasPhysicalVenue={hasAtLeastOnePhysicalVenue}
                hasVirtualOffers={hasAtLeastOneVirtualVenue}
                offererId={selectedOfferer.id}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}

OffererDetails.propTypes = {
  businessUnitList: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  handleChangeOfferer: PropTypes.func.isRequired,
  hasPhysicalVenues: PropTypes.bool.isRequired,
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
