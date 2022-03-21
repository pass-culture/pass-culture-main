import React, { FunctionComponent } from 'react'
import { Link } from 'react-router-dom'

import styles from './Hero.module.scss'
interface iHero {
  title: string
  text: string
  linkLabel: string
  linkTo: string
}

const Hero: FunctionComponent<iHero> = ({ title, text, linkLabel, linkTo }) => (
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
