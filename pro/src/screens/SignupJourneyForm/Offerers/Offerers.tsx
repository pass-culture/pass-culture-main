import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CreateOffererQueryModel } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { getSirenDataAdapter } from 'core/Offerers/adapters'
import { humanizeSiren } from 'core/Offerers/utils'
import { getVenuesOfOffererFromSiretAdapter } from 'core/Venue/adapters/getVenuesOfOffererFromSiretAdapter'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import { AddUserIcon, ArrowUpBIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar'

import styles from './Offerers.module.scss'

const Offerers = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const [isVenueListOpen, setIsVenueListOpen] = useState<boolean>(false)
  const [showLinkDialog, setShowLinkDialog] = useState<boolean>(false)

  const { offerer } = useSignupJourneyContext()

  /* istanbul ignore next: redirect to offerer if there is no siret */
  const {
    isLoading: isLoadingVenues,
    error: venuesOfOffererError,
    data: venuesOfOfferer,
  } = useAdapter(() =>
    getVenuesOfOffererFromSiretAdapter(offerer?.siret.replaceAll(' ', '') ?? '')
  )

  const formatedSiret = humanizeSiren(venuesOfOfferer?.offererSiren)
  const displayToggleVenueList =
    venuesOfOfferer && venuesOfOfferer?.venues.length > 5

  useEffect(() => {
    if (venuesOfOffererError || (!isLoadingVenues && !venuesOfOfferer)) {
      navigate('/parcours-inscription/structure')
    }
  }, [isLoadingVenues])

  if (isLoadingVenues) {
    return <Spinner />
  }

  const doLinkAccount = async () => {
    /* istanbul ignore next: venuesOfOfferer will always be defined here or else,
     the user would have been redirected */
    try {
      const response = await getSirenDataAdapter(
        venuesOfOfferer?.offererSiren ?? ''
      )
      const request: CreateOffererQueryModel = {
        city: response.payload.values?.city ?? '',
        name: venuesOfOfferer?.offererName ?? '',
        postalCode: response.payload.values?.postalCode ?? '',
        siren: venuesOfOfferer?.offererSiren ?? '',
      }
      await api.createOfferer(request)
      navigate('/parcours-inscription/structure/rattachement/confirmation')
    } catch (e) {
      notify.error('Impossible de lier votre compte à cette structure.')
    }
  }

  return (
    <div className={styles['existing-offerers-layout-wrapper']}>
      <div className={styles['existing-offerers-layout']}>
        <div className={styles['title-1']}>
          Nous avons trouvé un espace déjà inscrit sur le pass Culture et
          incluant ce SIRET.
        </div>
        <div className={styles['title-4']}>
          Rejoignez-le si votre structure se trouve dans la liste.
        </div>
        <div className={styles['venues-layout']}>
          <div className={styles['offerer-name-accent']}>
            {venuesOfOfferer?.offererName} - {formatedSiret}
          </div>
          <ul className={styles['venue-list']}>
            {venuesOfOfferer?.venues.map((venue, index) => (
              <li
                key={venue.id}
                hidden={
                  displayToggleVenueList && !isVenueListOpen && index >= 4
                }
              >
                {venue.name}
              </li>
            ))}
          </ul>
          {displayToggleVenueList && (
            <Button
              onClick={() => {
                setIsVenueListOpen(!isVenueListOpen)
              }}
              variant={ButtonVariant.TERNARY}
              Icon={() => (
                <ArrowUpBIcon
                  className={cn(styles['icon-more-venue'], {
                    [styles['icon-more-venue-down']]: isVenueListOpen,
                  })}
                />
              )}
            >
              {isVenueListOpen
                ? 'Afficher moins de structures'
                : 'Afficher plus de structures'}
            </Button>
          )}
        </div>
        <Button
          variant={ButtonVariant.PRIMARY}
          onClick={() => setShowLinkDialog(true)}
        >
          Rejoindre cet espace
        </Button>
      </div>
      <div className={cn(styles['wrong-offerer-title'], styles['title-4'])}>
        Votre structure ne se trouve pas dans cette liste ?
      </div>
      <Button
        className={styles['button-add-new-offerer']}
        onClick={() => navigate('/parcours-inscription/authentification')}
        variant={ButtonVariant.SECONDARY}
      >
        Ajouter une nouvelle structure
      </Button>
      <ActionBar
        previousStepTitle="Retour"
        hideRightButton
        onClickPrevious={() => navigate('/parcours-inscription/structure')}
        isDisabled={false}
      />
      {showLinkDialog && (
        <ConfirmDialog
          icon={AddUserIcon}
          onCancel={() => setShowLinkDialog(false)}
          title="Êtes-vous sûr de vouloir rejoindre cet espace ?"
          onConfirm={doLinkAccount}
          confirmText="Rejoindre cet espace"
          cancelText="Annuler"
          extraClassNames={styles['dialog-content']}
        >
          <div className={styles['dialog-subtitle']}>
            {venuesOfOfferer?.offererName} - {venuesOfOfferer?.offererSiren}
          </div>
          <div className={styles['dialog-info']}>
            Votre demande sera prise en compte et analysée par nos équipes.
          </div>
        </ConfirmDialog>
      )}
    </div>
  )
}

export default Offerers
