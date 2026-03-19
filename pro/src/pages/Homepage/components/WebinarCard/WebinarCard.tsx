import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import { HomepageVariant } from '../types'
import collective from './assets/collective.png'
import individual from './assets/individual.png'
import styles from './WebinarCard.module.scss'

export const WEBINAR_LINKS = {
  [HomepageVariant.COLLECTIVE]:
    'https://us06web.zoom.us/meeting/register/Bcw5SGLWSL-hcecl4d7e4w#/registration',
  [HomepageVariant.INDIVIDUAL]:
    'https://us06web.zoom.us/meeting/register/wtda-V2MQwmKKzkuvgpNlw#/registration',
}

export interface WebinarCardProps {
  variant: HomepageVariant
}

export const WebinarCard = ({ variant }: Readonly<WebinarCardProps>) => {
  const buttonLink = WEBINAR_LINKS[variant]
  const isCollective = variant === HomepageVariant.COLLECTIVE

  return (
    <Card variant="info">
      <img
        className={styles['webinar-image']}
        src={isCollective ? collective : individual}
        alt=""
        aria-hidden="true"
      />
      <Card.Header
        title={`Participer à nos webinaires sur la part ${
          isCollective ? 'collective' : 'individuelle'
        } !`}
        subtitle={
          isCollective
            ? 'Apprenez-en d’avantage sur nos fonctionnalités, la part collective et le paramétrage de votre compte.'
            : 'Découvrez nos fonctionnalités, les habitudes des jeunes, le paramétrage de votre compte.'
        }
      />
      <Card.Footer>
        <Button
          label="S’inscrire aux prochaines sessions"
          variant={ButtonVariant.SECONDARY}
          transparent
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          to={buttonLink}
          as="a"
          isExternal
          opensInNewTab
        />
      </Card.Footer>
    </Card>
  )
}
