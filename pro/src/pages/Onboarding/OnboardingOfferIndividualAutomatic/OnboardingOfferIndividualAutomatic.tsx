import cn from 'classnames'
import { useNavigate } from 'react-router-dom'

import { ActionBar } from '../components/ActionBar/ActionBar'
import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import styles from './OnboardingOfferIndividualAutomatic.module.scss'

interface OnboardingOfferIndividualAutomaticProps {
  className?: string
}

export const OnboardingOfferIndividualAutomatic = ({
  className,
}: OnboardingOfferIndividualAutomaticProps): JSX.Element => {
  const navigate = useNavigate()

  return (
    <OnboardingLayout>
      <div className={cn(className)}>
        <h1 className={styles['title']}>
          Connecter mon logiciel de gestion des stocks
        </h1>

        <p>Écran en cours de création. Veuillez revenir ultérieurement…</p>

        <ActionBar
          disableRightButton={true}
          withNextButton
          onLeftButtonClick={() => navigate('/onboarding/individuel')}
          onRightButtonClick={() => {}}
        />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividualAutomatic
