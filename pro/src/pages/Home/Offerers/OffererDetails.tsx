import React, { useEffect, useMemo, useState } from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as FullLink } from 'icons/full-link.svg'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'
import { Banner, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import { STEP_OFFERER_HASH } from '../HomepageBreadcrumb'

interface OffererDetailsProps {
  handleChangeOfferer: (event: React.ChangeEvent<HTMLSelectElement>) => void
  isUserOffererValidated: boolean
  offererOptions: SelectOption[]
  selectedOfferer: GetOffererResponseModel
}

const OffererDetails = ({
  handleChangeOfferer,
  isUserOffererValidated,
  offererOptions,
  selectedOfferer,
}: OffererDetailsProps) => {
  const { logEvent } = useAnalytics()

  const hasAtLeastOnePhysicalVenue = selectedOfferer.managedVenues
    ?.filter(venue => !venue.isVirtual)
    .map(venue => venue.id)
    .some(Boolean)

  const hasMissingReimbursementPoints = useMemo(() => {
    if (!selectedOfferer) {
      return false
    }
    return selectedOfferer.managedVenues
      ?.filter(venue => !venue.isVirtual)
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

  return (
    <div className="h-card h-card-secondary" data-testid="offerrer-wrapper">
      <div className={`h-card-inner${isExpanded && ' h-no-bottom'}`}>
        <div className="od-header-large">
          <div className="venue-select">
            <SelectInput
              onChange={handleChangeOfferer}
              id={STEP_OFFERER_HASH}
              name="offererId"
              options={offererOptions}
              value={selectedOfferer.nonHumanizedId.toString()}
            />
          </div>

          <div className="od-separator vertical" />
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
                offerer_id: selectedOfferer.nonHumanizedId,
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
                    Icon: FullLink,
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
                    Icon: FullLink,
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
                    Icon: FullLink,
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
            {showCreateVenueBanner && (
              <Banner
                type="notification-info"
                className="banner"
                links={[
                  {
                    href: `https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-`,
                    linkTitle: 'En savoir plus sur la création d’un lieu',
                    Icon: FullLink,
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
          </>
        )}
      </div>
    </div>
  )
}

export default OffererDetails
