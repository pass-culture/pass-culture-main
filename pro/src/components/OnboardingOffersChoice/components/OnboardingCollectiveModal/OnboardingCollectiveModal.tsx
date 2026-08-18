import { useState } from 'react'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { getUserDefaultPath } from '@/app/AppRouter/utils/getUserDefaultPath'
import { OnboardingDidacticEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setSelectedPartnerVenueById } from '@/commons/store/user/dispatchers/setSelectedPartnerVenueById'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import fullNextIcon from '@/icons/full-next.svg'

import acceptationIcon from './assets/acceptation.svg'
import calendarIcon from './assets/calendrier.svg'
import offerCreationIcon from './assets/creation_offre.svg'
import fileSubmissionIcon from './assets/depot_dossier.svg'
import styles from './OnboardingCollectiveModal.module.scss'

interface OnboardingCollectiveModalProps {
  isOpen: boolean
  onClose: () => void
}

export const OnboardingCollectiveModal = ({
  isOpen,
  onClose,
}: OnboardingCollectiveModalProps): JSX.Element => {
  const [notOnboardedError, setNotOnboardedError] = useState(false)
  const [genericError, setGenericError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const dispatch = useAppDispatch()

  const confirmAdageSubmission = async () => {
    logEvent(
      OnboardingDidacticEvents.HAS_CLICKED_ALREADY_SUBMITTED_COLLECTIVE_CASE_DIDACTIC_ONBOARDING
    )
    try {
      setNotOnboardedError(false)
      setGenericError(null)
      setIsLoading(true)

      if (!selectedPartnerVenue) {
        setIsLoading(false)
        setGenericError('Un problème est survenu, veuillez réessayer.')
        return
      }

      await api.synchronizeOffererOnboarding({
        path: {
          offerer_id: selectedPartnerVenue.managingOfferer.id,
        },
      })

      const { selectedPartnerVenue: updatedSelectedPartnerVenue } =
        await dispatch(
          setSelectedPartnerVenueById({
            nextSelectedPartnerVenueId: selectedPartnerVenue.id,
            shouldAlignSelectedAdminOfferer: false,
            shouldRefresh: true,
          })
        ).unwrap()

      if (updatedSelectedPartnerVenue?.isOnboarded) {
        return navigate(getUserDefaultPath())
      }

      // In any other case, it's an error
      setIsLoading(false)
      setNotOnboardedError(true)
    } catch {
      setIsLoading(false)
      setGenericError('Un problème est survenu, veuillez réessayer.')
    }
  }

  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={onClose}
      title="Déposer un dossier ADAGE"
      description="Pour continuer, vous devez compléter un dossier qui sera examiné par
          les services d'État pour vérifier votre éligibilité au dispositif pass
          Culture."
      primaryAction={
        <Button
          as="a"
          opensInNewTab
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.BRAND}
          onClick={() =>
            logEvent(
              OnboardingDidacticEvents.HAS_CLICKED_SUBMIT_COLLECTIVE_CASE_DIDACTIC_ONBOARDING
            )
          }
          to="https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage"
          label="Déposer un dossier"
          disabled={isLoading}
          fullWidth
        />
      }
      secondaryAction={
        <Button
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullNextIcon}
          onClick={confirmAdageSubmission}
          isLoading={isLoading}
          label="Vérifier si j'ai déposé un dossier"
        />
      }
      isFooterFixed
    >
      <div data-testid="onboarding-collective-modal">
        <hr className={styles['divider']} />
        {notOnboardedError && (
          <div className={styles['error-banner']}>
            <Banner
              variant={BannerVariants.ERROR}
              title="Aucun dossier n’a été déposé par votre structure"
              description="Pour créer des offres à destination des enseignants et des établissements scolaires, veuillez déposer un dossier."
            />
          </div>
        )}
        {genericError && (
          <div className={styles['error-banner']}>
            <Banner variant={BannerVariants.ERROR} title={genericError} />
          </div>
        )}
        <ol className={styles['onboarding-collective-steps']}>
          <ModalStep
            icon={fileSubmissionIcon}
            text="Dépôt du dossier de présentation de votre structure"
          />
          <ModalStep
            icon={acceptationIcon}
            text="Étude et validation du dossier en commission de votre territoire"
          />
          <ModalStep
            icon={offerCreationIcon}
            text="Création de vos offres sur le pass Culture Pro"
          />
          <ModalStep
            icon={calendarIcon}
            text="Réservation de vos offres par les enseignants sur ADAGE"
          />
        </ol>
      </div>
    </DetailedModal>
  )
}

function ModalStep({ icon, text }: Readonly<{ icon: string; text: string }>) {
  return (
    <li className={styles['onboarding-collective-step']}>
      <img
        src={icon}
        alt=""
        className={styles['onboarding-collective-step-icon']}
      />
      <p className={styles['onboarding-collective-step-text']}>{text}</p>
    </li>
  )
}
