import { DialogTitle } from '@radix-ui/react-dialog'
import cn from 'classnames'

import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import offerCreationWithAddressImageStatic from './assets/offer-creation-with-address-2x-static.png'
import offerCreationWithAddressImage from './assets/offer-creation-with-address-2x.gif'

import { useMediaQuery } from 'commons/hooks/useMediaQuery'
import styles from './DialogNoVenue.module.scss'

interface DialogNoVenueProps {
  className?: string
}

export const DialogNoVenue = ({
  className,
}: DialogNoVenueProps): JSX.Element => {
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)')
  return (
    <div className={cn(styles['dialog-content'], className)}>
      <div className={styles['dialog-image-wrapper']}>
        {prefersReducedMotion ? (
          <img
            src={offerCreationWithAddressImageStatic}
            alt="Sélection d’une adresse lors de la création d’offre"
            className={styles['dialog-image']}
          />
        ) : (
          <img
            src={offerCreationWithAddressImage}
            alt="Sélection d’une adresse lors de la création d’offre"
            className={styles['dialog-image']}
          />
        )}
      </div>

      <Tag variant={TagVariant.BLUE} className={styles['dialog-tag']}>
        Nouveau
      </Tag>
      <DialogTitle className={styles['dialog-title']}>
        Il n’est plus nécessaire de créer des lieux
      </DialogTitle>
      <p className={styles['dialog-text']}>
        Vous pouvez désormais créer une offre en la localisant à n’importe
        quelle adresse.
      </p>
      <ButtonLink
        className={styles['dialog-button']}
        variant={ButtonVariant.PRIMARY}
        to={'/offre/creation'}
      >
        Créer une offre
      </ButtonLink>
    </div>
  )
}
