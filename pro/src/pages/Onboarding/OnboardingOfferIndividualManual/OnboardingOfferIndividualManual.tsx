import cn from 'classnames'
import { useNavigate } from 'react-router-dom'

import { ActionBar } from '../components/ActionBar/ActionBar'
import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import styles from './OnboardingOfferIndividualManual.module.scss'

interface OnboardingOfferIndividualManualProps {
  className?: string
}

export const OnboardingOfferIndividualManual = ({
  className,
}: OnboardingOfferIndividualManualProps): JSX.Element => {
  const navigate = useNavigate()

  return (
    <OnboardingLayout showFooter={false}>
      <div className={cn(className)}>
        <h1 className={styles['title']}>Offre à destination des jeunes</h1>

        <p>Écran en cours de création. Veuillez revenir ultérieurement…</p>
      </div>

      <ActionBar
        disableRightButton={true}
        withNextButton
        onLeftButtonClick={() => navigate(-1)}
        onRightButtonClick={() => {}}
      />
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividualManual
