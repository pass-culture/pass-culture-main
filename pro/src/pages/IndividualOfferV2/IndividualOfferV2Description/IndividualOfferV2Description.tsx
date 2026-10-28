import { useNavigate } from 'react-router'

import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import strokeLeftIcon from '@/icons/stroke-left.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'

import styles from './IndividualOfferV2Description.module.scss'

const IndividualOfferV2Description = (): JSX.Element => {
  const navigate = useNavigate()

  return (
    <>
      <h2 className={styles['title']}>Description</h2>
      <ActionsBarSticky hasSideNav={false} isEmbedded={true}>
        <ActionsBarSticky.Left>
          <Button
            color={ButtonColor.NEUTRAL}
            variant={ButtonVariant.SECONDARY}
            onClick={async () => {
              await navigate(
                '/offre/individuelle/v2/creation/nature-format-domaine'
              )
            }}
            label="Étape précédente"
            icon={strokeLeftIcon}
            iconPosition={IconPositionEnum.LEFT}
          />
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <Button
            color={ButtonColor.BRAND}
            variant={ButtonVariant.PRIMARY}
            label="Étape suivante"
            icon={strokeRightIcon}
            iconPosition={IconPositionEnum.RIGHT}
          />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2Description
