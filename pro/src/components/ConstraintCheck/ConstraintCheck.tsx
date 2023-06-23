import React, { FunctionComponent } from 'react'

import { FieldError } from 'ui-kit/form/shared'

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
          <FieldError name={constraint.id}>{constraint.description}</FieldError>
        ) : (
          constraint.description
        )}
      </li>
    ))

  return <ul className={style['constraint-check']}>{fileConstraint()}</ul>
}
