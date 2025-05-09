import { Dialog } from 'components/Dialog/Dialog'
import strokeErrorIcon from 'icons/stroke-error.svg'
import { Button } from 'ui-kit/Button/Button'
import { LinkNode } from 'ui-kit/LinkNodes/LinkNodes'

import styles from './CollectiveBudgetInformation.module.scss'

type CollectiveBudgetDialogProps = {
  onClose: () => void
  open: boolean
}

export const CollectiveBudgetDialog = ({
  onClose,
  open,
}: CollectiveBudgetDialogProps) => {
  return (
    <Dialog
      title={
        'Informations importantes : crédit de la part collective du pass Culture 2024-2025'
      }
      icon={strokeErrorIcon}
      open={open}
      onCancel={onClose}
      explanation={
        "Dans une situation budgétaire inédite, le ministère de l’Éducation nationale doit maintenir strictement le budget alloué à la part collective du pass Culture. ll n'est plus possible d’effectuer de nouvelles réservations au titre de l’année scolaire 2024-2025. Cette situation ne concerne que les établissements publics et privés du second degré du ministère de l’Éducation nationale."
      }
    >
      <div className={styles['link-container']}>
        <LinkNode
          isExternal={true}
          href={
            'https://aide.passculture.app/hc/fr/articles/18234132822684--Acteurs-culturels-Informations-importantes-Cr%C3%A9dit-de-la-part-collective-pour-l-ann%C3%A9e-scolaire-2024-2025'
          }
          label={'En savoir plus'}
        />
      </div>
      <Button onClick={onClose}>Fermer</Button>
    </Dialog>
  )
}
