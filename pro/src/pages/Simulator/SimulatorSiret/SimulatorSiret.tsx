import { useNavigate } from 'react-router'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { SiretInputForm } from '@/components/SiretInputForm/SiretInputForm'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

export const SimulatorSiret = (): JSX.Element => {
  const navigate = useNavigate()
  const onSiretChecked = () => {
    // SAVE TO thing
    navigate('/inscription/preparation/activite')
  }

  const submitElement = (isSubmitting: boolean): JSX.Element => (
    <div className={commonStyles['action-bar']}>
      <Button
        as="a"
        to="/bienvenue/prochaines-etapes"
        variant={ButtonVariant.SECONDARY}
        label="Retour"
      />
      <BubbleStepper
        page={1}
        total={3}
        className={commonStyles['action-bar-stepper']}
      />
      <Button type="submit" label="Continuer" disabled={isSubmitting} />
    </div>
  )
  return (
    <div className={commonStyles['content']}>
      <h1 className={commonStyles['title']}>Renseignez votre SIRET</h1>
      <h2 className={commonStyles['subtitle']}>
        Le SIRET est un identifiant à 14 chiffres attribué à chaque structure.
        Vous le trouverez sur vos documents administratifs (avis de situation
        SIRENE, factures, contrats).
      </h2>
      <SiretInputForm
        submitElement={submitElement}
        initialValues={{ siret: '' }}
        onSiretChecked={onSiretChecked}
      />
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorSiret
