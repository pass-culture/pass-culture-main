import cn from 'classnames'
import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events, OffererLinkEvents } from 'core/FirebaseEvents/constants'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import fullAddUserIcon from 'icons/full-add-user.svg'
import fullEditIcon from 'icons/full-edit.svg'
import { updateSelectedOffererId } from 'store/user/reducer'
import { selectCurrentOffererId } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import { Card } from '../Card'

import styles from './OffererDetails.module.scss'

const CREATE_OFFERER_SELECT_ID = 'creation'

export interface OffererDetailsProps {
  isUserOffererValidated: boolean
  offererOptions: SelectOption[]
}

export const OffererDetails = ({
  isUserOffererValidated,
  offererOptions,
}: OffererDetailsProps) => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const dispatch = useDispatch()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const addOffererOption: SelectOption = {
    label: '+ Ajouter une structure',
    value: CREATE_OFFERER_SELECT_ID,
  }

  const handleChangeOfferer = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newOffererId = event.target.value
    if (newOffererId === CREATE_OFFERER_SELECT_ID) {
      navigate('/structures/creation')
    } else if (Number(newOffererId) !== selectedOffererId) {
      searchParams.set('structure', newOffererId)
      setSearchParams(searchParams)
      dispatch(updateSelectedOffererId(Number(newOffererId)))
      if (localStorageAvailable()) {
        localStorage.setItem(SAVED_OFFERER_ID_KEY, newOffererId)
      }
    }
  }

  return (
    <Card className={styles['card']} data-testid="offerrer-wrapper">
      <div className={styles['container']}>
        <div className={styles['offerer-select']}>
          <SelectInput
            onChange={handleChangeOfferer}
            name="offererId"
            data-testid="offerer-details-offerId"
            options={[...offererOptions, addOffererOption]}
            value={selectedOffererId ? String(selectedOffererId) : ''}
            aria-label="Structure"
          />
        </div>

        <div className={styles['venue-buttons']}>
          <div className={cn(styles['separator'])} />

          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `/structures/${selectedOffererId}`,
              isExternal: false,
            }}
            icon={fullAddUserIcon}
            isDisabled={!isUserOffererValidated}
            onClick={() => {
              logEvent(OffererLinkEvents.CLICKED_INVITE_COLLABORATOR, {
                offererId: selectedOffererId ?? undefined,
              })
            }}
          >
            Inviter
          </ButtonLink>

          <div className={cn(styles['separator'])} />

          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `/structures/${String(selectedOffererId)}`,
              isExternal: false,
            }}
            icon={fullEditIcon}
            isDisabled={!isUserOffererValidated}
            onClick={() =>
              logEvent(Events.CLICKED_MODIFY_OFFERER, {
                offerer_id: selectedOffererId ?? undefined,
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
