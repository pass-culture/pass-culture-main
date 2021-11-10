import React from 'react'

import styles from './Typography.module.scss'

interface ITypographyProps {
    level: 'h1' | 'h2' | 'h3' | 'h4';
    title: string
}

const Typography = ({ level, title }: ITypographyProps): JSX.Element => {
  switch(level) {
    case 'h1':
      return (
        <h1 className={styles.h1}>
          {title}
        </h1>
      )
    case 'h2':
      return (
        <h2 className={styles.h2}>
          {title}
        </h2>
      )
    case 'h3':
      return (
        <h3 className={styles.h3}>
          {title}
        </h3>
      )
    case 'h4':
      return (
        <h4 className={styles.h4}>
          {title}
        </h4>
      )
  }
}

export default Typography
