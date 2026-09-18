import { useEffect } from 'react'
import { useNavigate } from 'react-router'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import {
  SiretInputForm,
  type SiretInputFormValues,
} from '@/components/SiretInputForm/SiretInputForm'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'
import { useSimulatorContext } from '@/pages/Simulator/SimulatorContext'
import { Title } from '@/ui-kit/Title/Title'

import { saveSiretToStorage, tryRestoreSiretFromStorage } from '../storage'

export const SimulatorSiret = (): JSX.Element => {
  const navigate = useNavigate()
  const { siret, setSiret } = useSimulatorContext()

  useEffect(() => {
    try {
      tryRestoreSiretFromStorage(setSiret)
    } catch {
      // Nothing to do
    }
  }, [setSiret])

  const onSiretChecked = (formValues: SiretInputFormValues) => {
    saveSiretToStorage(formValues.siret)
    setSiret(formValues.siret)
    navigate('/inscription/preparation/accueil-public')
  }

  const submitElement = (isSubmitting: boolean): JSX.Element => (
    <div className={commonStyles['action-bar']}>
      <Button
        as="router-link"
        to="/bienvenue/prochaines-etapes"
        variant={ButtonVariant.SECONDARY}
        label="Retour"
      />
      <BubbleStepper
        page={1}
        total={4}
        className={commonStyles['action-bar-stepper']}
      />
      <Button type="submit" label="Continuer" disabled={isSubmitting} />
    </div>
  )
  return (
    <div className={commonStyles['content']}>
      <Title level="1" title="Renseignez votre SIRET" marginBottom="l" />
      <p className={commonStyles['subtitle']}>
        Le SIRET est un identifiant à 14 chiffres attribué à chaque structure.
        Vous le trouverez sur vos documents administratifs (avis de situation
        SIRENE, factures, contrats).
      </p>
      <SiretInputForm
        submitElement={submitElement}
        initialValues={{ siret: siret ?? '' }}
        onSiretChecked={onSiretChecked}
      />
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorSiret
