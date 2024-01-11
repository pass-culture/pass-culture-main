import cn from 'classnames'
import React from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { Events, OffererLinkEvents } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import useAnalytics from 'hooks/useAnalytics'
import fullAddUserIcon from 'icons/full-add-user.svg'
import fullEditIcon from 'icons/full-edit.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import { Card } from '../Card'

import styles from './OffererDetails.module.scss'

const CREATE_OFFERER_SELECT_ID = 'creation'

export interface OffererDetailsProps {
  isUserOffererValidated: boolean
  offererOptions: SelectOption[]
  selectedOfferer: GetOffererResponseModel
}

export const OffererDetails = ({
  isUserOffererValidated,
  offererOptions,
  selectedOfferer,
}: OffererDetailsProps) => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const addOffererOption: SelectOption = {
    label: '+ Ajouter une structure',
    value: CREATE_OFFERER_SELECT_ID,
  }

  const handleChangeOfferer = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newOffererId = event.target.value
    if (newOffererId === CREATE_OFFERER_SELECT_ID) {
      navigate('/structures/creation')
    } else if (newOffererId !== selectedOfferer?.id.toString()) {
      searchParams.set('structure', newOffererId)
      setSearchParams(searchParams)
    }
  }

  return (
    <Card className={styles['card']} data-testid="offerrer-wrapper">
      <div className={styles['container']}>
        <div className={styles['offerer-select']}>
          <SelectInput
            onChange={handleChangeOfferer}
            name="offererId"
            options={[...offererOptions, addOffererOption]}
            value={selectedOfferer.id.toString()}
            aria-label="Sélectionner une structure"
          />
        </div>

        <div className={styles['venue-buttons']}>
          <div className={cn(styles['separator'])} />

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

          <div className={cn(styles['separator'])} />

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
    </Card>
  )
}
