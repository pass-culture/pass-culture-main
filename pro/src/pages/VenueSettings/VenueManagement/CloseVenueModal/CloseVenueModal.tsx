import { useState } from 'react'

import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import fullWarningIcon from '@/icons/full-warning.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CloseVenueCard } from './CloseVenueCard/CloseVenueCard'
import styles from './CloseVenueModal.module.scss'

type CloseVenueModalProps = {
  isLastOpenedVenue: boolean
  name: string
  siret: string | null
  isOpen: boolean
  onCancel: () => void
  onValidate: () => void
}

export const CloseVenueModal = ({
  isLastOpenedVenue,
  name,
  siret,
  isOpen,
  onCancel,
  onValidate,
}: CloseVenueModalProps): JSX.Element => {
  const [isCertified, setIsCertified] = useState(false)
  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={onCancel}
      title="Vous souhaitez fermer votre structure ?"
      primaryAction={
        <Button
          disabled={!isCertified}
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.DANGER}
          onClick={onValidate}
          label="Confirmer la demande de fermeture"
        />
      }
      secondaryAction={
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={onCancel}
          label="Annuler"
        />
      }
      isFooterFixed
    >
      <div className={styles['modal-content']}>
        <Banner
          title="Un simple déménagement ou changement de SIRET ?"
          variant={BannerVariants.DEFAULT}
          description="Ne fermez pas votre structure. Modifiez simplement ces informations directement depuis les Paramètres généraux."
        />
        <div>
          <h3 className={styles['modal-content-subtitle']}>Les impacts :</h3>
          <ul className={styles['impact-list']}>
            <li>
              <span className={styles['impact-list-item']}>Offres :</span>{' '}
              Toutes vos offres publiées seront retirées de l'application et ne
              seront plus accessibles au public.
            </li>
            <li>
              <span className={styles['impact-list-item']}>Réservations :</span>{' '}
              Les réservations en cours seront automatiquement annulées.
            </li>
            <li>
              <span className={styles['impact-list-item']}>
                Remboursements :
              </span>{' '}
              Vos remboursements à venir seront honorés selon les conditions
              habituelles.
            </li>
            <li>
              <span className={styles['impact-list-item']}>Exports :</span>{' '}
              L'accès à vos exports de données reste accessible.
            </li>
          </ul>
        </div>
        <p className={styles['warning-message']}>
          <SvgIcon
            className={styles['warning-message-icon']}
            src={fullWarningIcon}
            alt=""
            width="20"
          />
          <span>
            Attention : la demande de fermeture de la structure est
            irréversible.
            {isLastOpenedVenue && (
              <>
                {' '}
                Vous n’aurez plus accès à votre compte 3 mois après votre
                demande !
              </>
            )}
          </span>
        </p>
        <CloseVenueCard
          name={name}
          siret={siret}
          certified={isCertified}
          onCertify={(certified) => setIsCertified(certified)}
        ></CloseVenueCard>
      </div>
    </DetailedModal>
  )
}
