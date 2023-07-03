import React from 'react'

import Dialog from 'components/Dialog/Dialog/Dialog'
import { ReactComponent as StrokeWarningIcon } from 'icons/stroke-warning.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './WrongStudentsModal.module.scss'

interface WrongStudentsModalProps {
  closeModal(): void
  postForm(): void
  modifyStudents(): void
  hasOnlyWrongStudents: boolean
}

const WrongStudentsModal = ({
  closeModal,
  postForm,
  modifyStudents,
  hasOnlyWrongStudents,
}: WrongStudentsModalProps) => {
  return (
    <Dialog
      onCancel={hasOnlyWrongStudents ? modifyStudents : closeModal}
      icon={StrokeWarningIcon}
      title="Cette offre ne peut pas s’adresser aux 6e et 5e"
      explanation={
        <>
          <p>
            Le dispositif pass Culture sera étendu aux classes de 6e et 5e à
            partir du{' '}
            <span className={style['wrong-student-modal-important']}>
              1er septembre 2023.
            </span>{' '}
            Pour créer une offre à destination de ces niveaux scolaires, vous
            devez proposer une date à partir du <br />
            1er septembre 2023.
          </p>
          {!hasOnlyWrongStudents && (
            <>
              <br />
              <p>
                Sinon, vous pouvez créer cette offre sans les classes de 6e et
                5e.
              </p>
            </>
          )}
        </>
      }
    >
      <div className={style['wrong-students-modal-actions']}>
        <Button
          onClick={hasOnlyWrongStudents ? modifyStudents : closeModal}
          variant={ButtonVariant.SECONDARY}
        >
          {hasOnlyWrongStudents
            ? 'Modifier les participants'
            : 'Modifier la date'}
        </Button>
        <Button
          onClick={hasOnlyWrongStudents ? closeModal : postForm}
          variant={ButtonVariant.SECONDARY}
        >
          {hasOnlyWrongStudents ? 'Modifier la date' : 'Enlever les 6e et 5e'}
        </Button>
      </div>
    </Dialog>
  )
}

export default WrongStudentsModal
