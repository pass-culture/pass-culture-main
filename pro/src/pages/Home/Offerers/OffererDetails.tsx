import React, { useMemo } from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import { Events, OffererLinkEvents } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullAddUserIcon from 'icons/full-add-user.svg'
import fullEditIcon from 'icons/full-edit.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import { STEP_OFFERER_HASH } from '../HomepageBreadcrumb'

import { OffererBanners } from './OffererBanners'

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
  const isStatisticsDashboardEnabled = useActiveFeature('WIP_HOME_STATS')
  const isNewOffererLinkEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_USER_OFFERER_LINK'
  )

  const hasAtLeastOnePhysicalVenue = selectedOfferer.managedVenues
    ?.filter((venue) => !venue.isVirtual)
    .map((venue) => venue.id)
    .some(Boolean)

  const hasMissingReimbursementPoints = useMemo(() => {
    if (!selectedOfferer) {
      return false
    }
    return selectedOfferer.managedVenues
      ?.filter((venue) => !venue.isVirtual)
      .map((venue) => venue.hasMissingReimbursementPoint)
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

  const isExpanded =
    hasMissingReimbursementPoints ||
    !isUserOffererValidated ||
    showCreateVenueBanner ||
    showMissingReimbursmentPointsBanner ||
    showOffererNotValidatedAndNoPhysicalVenue ||
    showOffererNotValidatedAndPhysicalVenue

  return (
    <div className="h-card h-card-secondary" data-testid="offerrer-wrapper">
      <div className="h-card-inner h-no-bottom">
        <div className="od-header-large">
          <div className="venue-select">
            <SelectInput
              onChange={handleChangeOfferer}
              id={STEP_OFFERER_HASH}
              name="offererId"
              options={offererOptions}
              value={selectedOfferer.id.toString()}
            />
          </div>

          {isNewOffererLinkEnabled && (
            <>
              <div className="od-separator vertical" />
              <ButtonLink
                variant={ButtonVariant.TERNARY}
                link={{
                  to: `/structures/${selectedOfferer.id}`,
                  isExternal: false,
                }}
                icon={fullAddUserIcon}
                isDisabled={!isUserOffererValidated}
                onClick={() => {
                  logEvent?.(OffererLinkEvents.CLICKED_INVITE_COLLABORATOR, {
                    offererId: selectedOfferer.id,
                  })
                }}
              >
                Inviter
              </ButtonLink>
            </>
          )}

          <div className="od-separator vertical" />
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `/structures/${selectedOfferer.id}`,
              isExternal: false,
            }}
            icon={fullEditIcon}
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

        {isExpanded && !isStatisticsDashboardEnabled && (
          <>
            <div className="od-separator horizontal" />
            <OffererBanners
              selectedOfferer={selectedOfferer}
              isUserOffererValidated={isUserOffererValidated}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default OffererDetails
