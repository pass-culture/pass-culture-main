import React, { FunctionComponent, useState } from 'react'

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
  onSetImage: (file: File) => void
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
        <Advices hidden={hidden} setHidden={setHidden} />
      </form>
    </section>
  )
}
