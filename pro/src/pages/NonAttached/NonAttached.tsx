import { useNavigate } from 'react-router'

import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { Newsletter } from '@/components/Newsletter/Newsletter'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'

import { NonAttachedBanner } from '../../components/NonAttachedBanner/NonAttachedBanner'
import styles from './NonAttached.module.scss'

const NonAttached = () => {
  const navigate = useNavigate()

  return (
    <OnboardingLayout
      isEntryScreen
      mainHeading="Bienvenue sur votre espace partenaire"
    >
      <div className={styles['wrapper']}>
        <Button
          onClick={() => navigate('/hub')}
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullBackIcon}
          iconPosition={IconPositionEnum.LEFT}
          label="Retour vers la sélection du partenaire"
        />
        <NonAttachedBanner />
        <Newsletter />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = NonAttached
