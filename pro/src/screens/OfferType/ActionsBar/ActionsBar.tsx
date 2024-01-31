import ActionsBarSticky from 'components/ActionsBarSticky'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullRightIcon from 'icons/full-right.svg'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

interface ActionsBarProps {
  disableNextButton?: boolean
}

const ActionsBar = ({
  disableNextButton = false,
}: ActionsBarProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          link={{ to: '/offres', isExternal: false }}
          variant={ButtonVariant.SECONDARY}
          onClick={() => logEvent?.(Events.CLICKED_CANCEL_OFFER_CREATION)}
        >
          Annuler et quitter
        </ButtonLink>
      </ActionsBarSticky.Left>
      <ActionsBarSticky.Right>
        <SubmitButton
          icon={fullRightIcon}
          iconPosition={IconPositionEnum.RIGHT}
          disabled={disableNextButton}
        >
          Étape suivante
        </SubmitButton>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

export default ActionsBar
