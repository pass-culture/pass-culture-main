import cn from 'classnames'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { ShareTemplateOfferLink } from '@/components/CollectiveOffer/ShareTemplateOfferLink/ShareTemplateOfferLink'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
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
  const isCollectiveOfferTemplateShareLinkEnabled = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_OFFER_TEMPLATE_SHARE_LINK'
  )

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
        ? isCollectiveOfferTemplateShareLinkEnabled && canShareOffer
          ? showcaseOfferWithShareLink(offer)
          : showcaseOffer()
        : activeOffer(offer)

  return (
    <BasicLayout
      mainHeading={confirmationData.title}
      mainSubHeading={
        isCollectiveOfferTemplateShareLinkEnabled ? offer.name : undefined
      }
    >
      <div className={styles['confirmation-wrapper']}>
        <div className={styles['confirmation']}>
          {confirmationData.icon}
          <div>{confirmationData.description}</div>
          <div className={styles['confirmation-actions']}>
            <ButtonLink
              variant={ButtonVariant.SECONDARY}
              className={styles['confirmation-action']}
              to={isShowcase ? '/offres/vitrines' : '/offres/collectives'}
            >
              Voir mes offres
            </ButtonLink>
            <ButtonLink
              variant={ButtonVariant.PRIMARY}
              className={styles['confirmation-action']}
              to={`/offre/creation${offererId ? `?structure=${offererId}` : ''}`}
            >
              Créer une nouvelle offre
            </ButtonLink>
          </div>
        </div>

        {!isCollectiveOfferTemplateShareLinkEnabled && (
          <div className={styles['confirmation-banner']}>
            <Banner
              title="Quelle est la prochaine étape ?"
              actions={[
                {
                  href: `https://aide.passculture.app/hc/fr/articles/4416082284945--Acteurs-Culturels-Quel-est-le-cycle-de-vie-de-mon-offre-collective-de-sa-cr%C3%A9ation-%C3%A0-son-remboursement`,
                  label:
                    'Quel est le cycle de vie d’une offre collective, de sa création à son remboursement',
                  isExternal: true,
                  type: 'link',
                  icon: fullLinkIcon,
                  iconAlt: 'Nouvelle fenêtre',
                },
              ]}
              description={
                <>
                  {isShowcase ? (
                    <>
                      <p>
                        Les enseignants intéressés par votre offre vitrine vous
                        contacterons par mail ou téléphone.
                      </p>
                      <p>
                        Après un accord mutuel, vous pourrez créer une offre
                        réservable en complétant la date, le prix et
                        l’établissement convenus avec l’enseignant.{' '}
                      </p>
                      <p>
                        Cette nouvelle offre apparaitra sur ADAGE et pourra être
                        préréservée par l’enseignant.
                      </p>
                    </>
                  ) : (
                    <>
                      <p>
                        L’enseignant doit préréserver votre offre depuis son
                        compte ADAGE.
                      </p>
                      <p>
                        Une fois la préréservation faite, vous verrez une
                        réservation portant le statut préréservé qui, dans un
                        second temps, devra être officiellement réservée par le
                        chef d’établissement.
                      </p>
                    </>
                  )}
                </>
              }
            />
          </div>
        )}
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
