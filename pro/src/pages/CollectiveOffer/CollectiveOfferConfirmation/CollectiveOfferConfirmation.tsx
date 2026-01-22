import cn from 'classnames'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { ShareTemplateOfferLink } from '@/components/CollectiveOffer/ShareTemplateOfferLink/ShareTemplateOfferLink'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullValidateIcon from '@/icons/full-validate.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import styles from './CollectiveOfferConfirmation.module.scss'

function getInstitutionDisplayName(
  offer: MandatoryCollectiveOfferFromParamsProps['offer']
) {
  if (isCollectiveOfferTemplate(offer)) {
    return ''
  }

  if (!offer.institution) {
    return ''
  }
  return `${offer.institution.institutionType ?? ''} ${offer.institution.name}`.trim()
}

const activeOffer = (
  offer: MandatoryCollectiveOfferFromParamsProps['offer']
) => ({
  title: 'Votre offre a été publiée sur ADAGE',
  description: (
    <>
      Votre offre est désormais visible et réservable par les enseignants et
      chefs d’établissements{' '}
      {getInstitutionDisplayName(offer) ? (
        <>
          de l’établissement scolaire :{' '}
          <span className={styles['institution-name']}>
            {getInstitutionDisplayName(offer)}
          </span>
        </>
      ) : (
        'des établissement scolaires qui sont dans la ou les zones de mobilité sélectionnées.'
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
      <p>Nous vérifions actuellement la conformité de votre offre.</p>
      <p className={styles['text-bold']}>
        Cette vérification pourra prendre jusqu’à 72h.
      </p>
      <p className={styles['text-bold']}>
        Vous ne pouvez pas effectuer de modification pour l’instant.
      </p>
      <p>
        Vous recevrez un e-mail de confirmation une fois votre offre validée.
      </p>
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

const showcaseOffer = () => ({
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
})

const showcaseOfferWithShareLink = (
  offer: MandatoryCollectiveOfferFromParamsProps['offer']
) => ({
  title: 'Créer une offre',
  description: (
    <>
      <div className={styles['confirmation-title']}>
        Votre offre a été publiée sur ADAGE
      </div>
      <div className={styles['confirmation-description']}>
        <span className={styles['confirmation-description-instruction']}>
          Aidez les enseignants à retrouver votre offre plus facilement sur
          ADAGE
        </span>
        <ShareTemplateOfferLink offerId={offer.id} />
      </div>
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

const CollectiveOfferConfirmation = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const isShowcase = offer.isTemplate
  const offerStatus = offer.displayedStatus
  const offererId = offer.venue.managingOfferer.id

  const canShareOffer =
    isCollectiveOfferTemplate(offer) &&
    offer.allowedActions.includes(
      CollectiveOfferTemplateAllowedAction.CAN_SHARE
    )

  const confirmationData =
    offerStatus === CollectiveOfferDisplayedStatus.UNDER_REVIEW
      ? pendingOffer
      : isShowcase
        ? canShareOffer
          ? showcaseOfferWithShareLink(offer)
          : showcaseOffer()
        : activeOffer(offer)

  return (
    <BasicLayout
      mainHeading={confirmationData.title}
      mainSubHeading={offer.name}
    >
      <div className={styles['confirmation-wrapper']}>
        <div className={styles['confirmation']}>
          {confirmationData.icon}
          <div>{confirmationData.description}</div>
          <div className={styles['confirmation-actions']}>
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              to={isShowcase ? '/offres/vitrines' : '/offres/collectives'}
              label="Voir mes offres"
            />
            <Button
              as="a"
              variant={ButtonVariant.PRIMARY}
              to={`/offre/creation${offererId ? `?structure=${offererId}` : ''}`}
              label="Créer une nouvelle offre"
            />
          </div>
        </div>
      </div>
      <RouteLeavingGuardCollectiveOfferCreation when={false} />
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferConfirmation
)
