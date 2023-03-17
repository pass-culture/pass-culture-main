import React from 'react'
import { Link } from 'react-router-dom'

import styles from './Hero.module.scss'

interface IHero {
  title: string
  text: string
  linkLabel: string
  linkTo: string
}

const Hero = ({ title, text, linkLabel, linkTo }: IHero): JSX.Element => (
  <section className={styles['hero']}>
    <div className={styles['hero-body']}>
      <h1>{title}</h1>
      <h2>{text}</h2>
      <Link className="primary-link" to={linkTo}>
        {linkLabel}
      </Link>
    </div>
  </section>
)
export default Hero
