import { Button } from '@/design-system/Button/Button'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokeErrorIcon from '@/icons/stroke-error.svg'

type ConfirmVenueClosedModalProps = {
  isPricingPoint: boolean
  onValidate: () => void
  isOpen: boolean
}

export const ConfirmVenueClosedModal = ({
  isPricingPoint,
  onValidate,
  isOpen,
}: ConfirmVenueClosedModalProps): JSX.Element => {
  return (
    <SimpleModal
      iconPath={strokeErrorIcon}
      title="Votre demande de fermeture a bien été prise en compte."
      isOpen={isOpen}
      onClose={onValidate}
      actionButtons={[
        <Button onClick={onValidate} label="J'ai compris" key="confirm" />,
      ]}
    >
      <p>
        {isPricingPoint
          ? 'Votre demande de fermeture est en cours de traitement. Nos équipes Support reviendront vers vous ultérieurement.'
          : 'Les impacts suite à la fermeture de votre structure prendront effet dans les prochaines heures. Si ce n’est pas le cas, merci de contacter nos équipes.'}
      </p>
    </SimpleModal>
  )
}
