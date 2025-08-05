import { api } from 'apiClient/api'
import { useAnalytics } from 'app/App/analytics/firebase'
import cn from 'classnames'
import { OnboardingDidacticEvents } from 'commons/core/FirebaseEvents/constants'
import { updateCurrentOffererOnboardingStatus } from 'commons/store/offerer/reducer'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import fullNextIcon from 'icons/full-next.svg'
import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import acceptationIcon from './assets/acceptation.svg'
import calendarIcon from './assets/calendrier.svg'
import offerCreationIcon from './assets/creation_offre.svg'
import fileSubmissionIcon from './assets/depot_dossier.svg'
import styles from './OnboardingCollectiveModal.module.scss'

interface OnboardingCollectiveModalProps {
  className?: string
}

export const OnboardingCollectiveModal = ({
  className,
}: OnboardingCollectiveModalProps): JSX.Element => {
  const [errorMessage, setErrorMessage] = useState<null | string>(null)
  const [isLoading, setIsLoading] = useState(false)
  const currentOffererId = useSelector(selectCurrentOffererId)
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const dispatch = useDispatch()

  if (currentOffererId === null) {
    return <Spinner />
  }

  const checkEligibility = async () => {
    logEvent(
      OnboardingDidacticEvents.HAS_CLICKED_ALREADY_SUBMITTED_COLLECTIVE_CASE_DIDACTIC_ONBOARDING
    )
    try {
      setErrorMessage(null)
      setIsLoading(true)
      const eligibility = await api.getOffererEligibility(currentOffererId)
      if (eligibility.isOnboarded) {
        dispatch(updateCurrentOffererOnboardingStatus(true))
        return navigate('/accueil')
      }

      // In any other case, it's an error
      setIsLoading(false)
      setErrorMessage('Aucun dossier n’a été déposé par votre structure.')
    } catch {
      setIsLoading(false)
      setErrorMessage('Un problème est survenu, veuillez réessayer.')
    }
  }

  return (
    <div
      className={cn(styles[`onboarding-collective-modal`], className)}
      data-testid="onboarding-collective-modal"
    >
      <h1 className={styles['onboarding-collective-title']}>
        Quelles sont les étapes ?
      </h1>
      <p className={styles['onboarding-collective-text']}>
        Pour continuer, vous devez compléter un dossier qui sera examiné par les
        services d’État pour vérifier votre éligibilité au dispositif pass
        Culture.
      </p>
      <div className={styles['onboarding-collective-steps']}>
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
      </div>
      <div className={styles['onboarding-collective-actions']}>
        <ButtonLink
          isExternal
          opensInNewTab
          className={styles['onboarding-collective-button']}
          variant={ButtonVariant.PRIMARY}
          onClick={() =>
            logEvent(
              OnboardingDidacticEvents.HAS_CLICKED_SUBMIT_COLLECTIVE_CASE_DIDACTIC_ONBOARDING
            )
          }
          to="https://www.demarches-simplifiees.fr/commencer/demande-de-referencement-sur-adage"
        >
          Déposer un dossier
        </ButtonLink>
        <Button
          className={styles['onboarding-collective-button']}
          variant={ButtonVariant.TERNARY}
          icon={fullNextIcon}
          onClick={checkEligibility}
          disabled={isLoading}
        >
          {isLoading ? (
            <>Vérification en cours …</>
          ) : (
            <>J’ai déposé un dossier</>
          )}
        </Button>
      </div>
      {errorMessage && (
        <div className={styles['error-message']}>{errorMessage}</div>
      )}
    </div>
  )
}

function ModalStep({ icon, text }: { icon: string; text: string }) {
  return (
    <div className={styles['onboarding-collective-step']}>
      <img
        src={icon}
        alt=""
        className={styles['onboarding-collective-step-icon']}
      />
      <p className={styles['onboarding-collective-step-text']}>{text}</p>
    </div>
  )
}
