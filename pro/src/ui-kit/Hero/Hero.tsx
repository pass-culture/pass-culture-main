import React from 'react'

import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './Hero.module.scss'

export interface HeroProps {
  title: string
  text: string
  linkLabel: string
  linkTo: string
}

const Hero = ({ title, text, linkLabel, linkTo }: HeroProps): JSX.Element => (
  <section className={styles['hero']}>
    <div className={styles['hero-body']}>
      <h1>{title}</h1>
      <h2>{text}</h2>
      <ButtonLink
        variant={ButtonVariant.PRIMARY}
        link={{ isExternal: false, to: linkTo }}
      >
        {linkLabel}
      </ButtonLink>
    </div>
  </section>
)
export default Hero
