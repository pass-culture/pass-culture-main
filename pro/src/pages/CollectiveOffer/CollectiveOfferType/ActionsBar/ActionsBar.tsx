import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullRightIcon from '@/icons/full-right.svg'

interface ActionsBarProps {
  disableNextButton?: boolean
}

export const ActionsBar = ({
  disableNextButton = false,
}: ActionsBarProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <Button
          as="router-link"
          to={computeIndividualOffersUrl({})}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={() => logEvent(Events.CLICKED_CANCEL_OFFER_CREATION)}
          label="Annuler et quitter"
        />
      </ActionsBarSticky.Left>
      <ActionsBarSticky.Right>
        <Button
          type="submit"
          icon={fullRightIcon}
          iconPosition={IconPositionEnum.RIGHT}
          disabled={disableNextButton}
          label="Étape suivante"
        />
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
