import cn from 'classnames'
import React from 'react'

import { CollectiveOfferStatus } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import fullValidateIcon from 'icons/full-validate.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CollectiveOfferConfirmation.module.scss'

interface CollectiveOfferConfirmationProps {
  offererId?: number | null
  offerStatus?: CollectiveOfferStatus
  isShowcase?: boolean
  institutionDisplayName?: string
}

const activeOffer = (institutionDisplayName?: string) => ({
  title: 'Votre offre a été publiée sur ADAGE',
  description: (
    <>
      Votre offre est désormais visible et réservable par les enseignants et
      chefs d’établissements{' '}
      {institutionDisplayName ? (
        <>
          de l’établissement scolaire :
          <br />
          <br />
          <b>{institutionDisplayName}</b>
        </>
      ) : (
        <>
          des établissement scolaires qui sont dans la ou les zones de mobilité
          sélectionnées.
        </>
      )}
    </>
  ),
  icon: (
    <SvgIcon
      src={fullValidateIcon}
      alt=""
      className={cn(
        styles['confirmation-icon'],
        styles['confirmation-icon-validate']
      )}
    />
  ),
})

const pendingOffer = {
  title: 'Offre en cours de validation !',
  description: (
    <>
      Votre offre est en cours de validation par l’équipe pass Culture, nous
      vérifions actuellement son éligibilité. Cette vérification pourra prendre
      jusqu’à 72h.
    </>
  ),
  icon: (
    <SvgIcon
      src={fullWaitIcon}
      alt=""
      className={styles['confirmation-icon']}
    />
  ),
}

const showcaseOffer = {
  title: 'Votre offre a été publiée sur ADAGE',
  description: (
    <>
      Votre offre est visible uniquement par les enseignants et chefs
      d’établissement de l’Éducation Nationale qui peuvent désormais prendre
      contact avec vous pour co-construire une offre adaptée à leurs classes.
    </>
  ),
  icon: (
    <SvgIcon
      src={fullValidateIcon}
      alt=""
      className={cn(
        styles['confirmation-icon'],
        styles['confirmation-icon-validate']
      )}
    />
  ),
}

const mapOfferStatusToData = (
  status?: CollectiveOfferStatus,
  isShowcase?: boolean,
  institutionName?: string
) => {
  if (status === CollectiveOfferStatus.PENDING) {
    return pendingOffer
  }

  if (isShowcase) {
    return showcaseOffer
  }

  return activeOffer(institutionName)
}

export const CollectiveOfferConfirmationScreen = ({
  offererId,
  offerStatus,
  isShowcase,
  institutionDisplayName,
}: CollectiveOfferConfirmationProps): JSX.Element => {
  const { title, description, icon } = mapOfferStatusToData(
    offerStatus,
    isShowcase,
    institutionDisplayName
  )

  return (
    <div className={styles['confirmation-wrapper']}>
      <div className={styles['confirmation']}>
        {icon}
        <div className={styles['confirmation-section']}>
          <div className={styles['confirmation-section-header']}>
            <h1 className={styles['confirmation-section-title']}>{title}</h1>
          </div>
          <p className={styles['form-layout-section-description']}>
            {description}
          </p>
        </div>
        <div className={styles['confirmation-actions']}>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            className={styles['confirmation-action']}
            link={{ to: '/offres/collectives', isExternal: false }}
          >
            Voir mes offres
          </ButtonLink>
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            className={styles['confirmation-action']}
            link={{
              to: `/offre/creation${
                offererId ? `?structure=${offererId}` : ''
              }`,
              isExternal: false,
            }}
          >
            Créer une nouvelle offre
          </ButtonLink>
        </div>
      </div>

      <Callout
        className={styles['confirmation-banner']}
        links={[
          {
            href: `https://aide.passculture.app/hc/fr/articles/4416082284945--Acteurs-Culturels-Quel-est-le-cycle-de-vie-de-mon-offre-collective-de-sa-cr%C3%A9ation-%C3%A0-son-remboursement`,
            label:
              'Quel est le cycle de vie d’une offre collective, de sa création à son remboursement',
            isExternal: true,
          },
        ]}
      >
        <h2 className={styles['confirmation-banner-title']}>
          Quelle est la prochaine étape ?
        </h2>
        {isShowcase ? (
          <>
            Les enseignants intéressés par votre offre vitrine vous contacterons
            par mail ou téléphone. <br />
            Après un accord mutuel, vous pourrez créer une offre réservable en
            complétant la date, le prix et l’établissement convenus avec
            l’enseignant. <br />
            Cette nouvelle offre apparaitra sur ADAGE et pourra être préréservée
            par l’enseignant.
          </>
        ) : (
          <>
            L’enseignant doit préréserver votre offre depuis son compte ADAGE.
            <br />
            Une fois la préréservation faite, vous verrez une réservation
            portant le statut préréservé qui, dans un second temps, devra être
            officiellement réservée par le chef d’établissement.
          </>
        )}
      </Callout>
    </div>
  )
}
