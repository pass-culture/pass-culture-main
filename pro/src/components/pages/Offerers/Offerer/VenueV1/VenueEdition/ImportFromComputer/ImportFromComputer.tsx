import React, { FunctionComponent, useState } from 'react'

import { NBSP } from 'core/shared'
import Advices from 'new_components/Advices/Advices'
import { ConstraintCheck } from 'new_components/ConstraintCheck/ConstraintCheck'
import { Constraint } from 'new_components/ConstraintCheck/imageConstraints'
import { useCheckAndSetImage } from 'new_components/ConstraintCheck/useCheckAndSetImage'
import { ImportFromComputerInput } from 'new_components/ImportFromComputerInput/ImportFromComputerInput'
import { PreferredOrientation } from 'new_components/PreferredOrientation/PreferredOrientation'
import { Divider } from 'ui-kit'

import style from './ImportFromComputer.module.scss'

export type ImportFromComputerProps = {
  orientation: 'portrait' | 'landscape'
  imageTypes: string[]
  constraints: Constraint[]
  onSetImage: (file: string) => void
  children?: never
}

export const ImportFromComputer: FunctionComponent<ImportFromComputerProps> = ({
  constraints,
  imageTypes,
  orientation,
  onSetImage,
}) => {
  const [hidden, setHidden] = useState(true)
  const { errors, checkAndSetImage } = useCheckAndSetImage({
    constraints,
    onSetImage,
  })

  const advicesDescription = `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui représente votre lieu. Si vous n'avez pas d'image de votre lieu ou si vous cherchez de bons exemples, les banques d'images suivantes sont à votre disposition${NBSP}:`

  return (
    <section className={style['import-from-computer']}>
      <form action="#" className={style['import-from-computer']}>
        <header>
          <h1 className={style['import-from-computer-header']}>
            Ajouter une image
          </h1>
        </header>
        <PreferredOrientation orientation={orientation} />
        <ImportFromComputerInput
          imageTypes={imageTypes}
          isValid={!errors}
          onSetImage={checkAndSetImage}
        />
        <ConstraintCheck
          constraints={constraints}
          failingConstraints={errors}
        />
        <Divider
          className={style['import-from-computer-horizontal-rule']}
          size="large"
        />
        <Advices
          hidden={hidden}
          setHidden={setHidden}
          teaserText={advicesDescription}
        />
      </form>
    </section>
  )
}
