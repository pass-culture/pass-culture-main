import React, { FunctionComponent } from 'react'

import Icon from 'components/layout/Icon'

import style from './ConstraintCheck.module.scss'
import { Constraint } from './imageConstraints'

export type ConstraintCheckProps = {
  constraints: Constraint[]
  failingConstraints: string[]
  children?: never
}

export const ConstraintCheck: FunctionComponent<ConstraintCheckProps> = ({
  constraints,
  failingConstraints,
}) => {
  const fileConstraint = () =>
    constraints.map(constraint => (
      <li key={constraint.id}>
        {failingConstraints.includes(constraint.id) ? (
          <strong
            aria-live="assertive"
            aria-relevant="all"
            className={style['constraint-check-failing-constraint']}
          >
            <Icon svg="ico-notification-error-red" />
            {constraint.description}
          </strong>
        ) : (
          constraint.description
        )}
      </li>
    ))

  return <ul className={style['constraint-check']}>{fileConstraint()}</ul>
}
