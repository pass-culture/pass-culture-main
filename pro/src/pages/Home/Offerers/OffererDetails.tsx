import cn from 'classnames'
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

import { Card } from '../Card'
import { hasOffererAtLeastOnePhysicalVenue } from '../venueUtils'

import { OffererBanners } from './OffererBanners'
import styles from './OffererDetails.module.scss'

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

  const hasMissingReimbursementPoints = useMemo(() => {
    if (!selectedOfferer) {
      return false
    }
    return selectedOfferer.managedVenues
      ?.filter((venue) => !venue.isVirtual)
      .map((venue) => venue.hasMissingReimbursementPoint)
      .some(Boolean)
  }, [selectedOfferer])

  const hasAtLeastOnePhysicalVenue =
    hasOffererAtLeastOnePhysicalVenue(selectedOfferer)

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
    <Card className={styles['card']} data-testid="offerrer-wrapper">
      <div className={styles['container']}>
        <div className={styles['offerer-select']}>
          <SelectInput
            onChange={handleChangeOfferer}
            name="offererId"
            options={offererOptions}
            value={selectedOfferer.id.toString()}
            title="Structure"
          />
        </div>

        <div className={styles['venue-buttons']}>
          <div className={cn(styles['separator'], styles['vertical'])} />

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

          <div className={cn(styles['separator'], styles['vertical'])} />

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
      </div>

      {isExpanded && !isStatisticsDashboardEnabled && (
        <>
          <div className={cn(styles['separator'], styles['horizontal'])} />
          <OffererBanners
            offerer={selectedOfferer}
            isUserOffererValidated={isUserOffererValidated}
          />
        </>
      )}
    </Card>
  )
}

export default OffererDetails
