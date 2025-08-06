import { FunctionComponent } from 'react'

import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'

import style from './ConstraintCheck.module.scss'
import { Constraint } from './imageConstraints'

type ConstraintCheckProps = {
  constraints: Constraint[]
  failingConstraints: string[]
  children?: never
  id: string
}

export const ConstraintCheck: FunctionComponent<ConstraintCheckProps> = ({
  constraints,
  failingConstraints,
  id,
}) => {
  const fileConstraint = () =>
    constraints.map((constraint) => (
      <li key={constraint.id}>
        {failingConstraints.includes(constraint.id) ? (
          <FieldError iconAlt="Erreur" name={constraint.id}>
            {constraint.description}
          </FieldError>
        ) : (
          constraint.description
        )}
      </li>
    ))

  return (
    <ul
      id={id}
      className={style['constraint-check']}
      role="alert"
      aria-relevant="additions"
    >
      {fileConstraint()}
    </ul>
  )
}
