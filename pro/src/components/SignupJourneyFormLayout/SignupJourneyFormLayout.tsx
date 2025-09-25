import classNames from 'classnames'
import { type JSX, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { SignupJourneyStepper } from '@/components/SignupJourneyStepper/SignupJourneyStepper'

import styles from './SignupJourneyFormLayoutContent.module.scss'

interface SignupOffererFormLayoutProps {
  children: React.ReactNode
  className?: string
}

export const SignupJourneyFormLayout = ({
  children,
}: SignupOffererFormLayoutProps): JSX.Element => {
  const location = useLocation()
  const navigate = useNavigate()
  const { offerer, setOfferer } = useSignupJourneyContext()

  useEffect(() => {
    if (!location.pathname.includes('/inscription/structure/recherche')) {
      if (offerer?.siret === '' || offerer?.siren === '') {
        setOfferer(null)
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate('/inscription/structure/recherche')
      }
    }
  }, [offerer?.siren, offerer?.siret, location.pathname, navigate, setOfferer])

  return (
    <div
      className={classNames({
        [styles['signup-offerer-layout-wrapper-with-footer']]: true,
      })}
    >
      <SignupJourneyStepper />
      {children}
    </div>
  )
}
