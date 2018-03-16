import classnames from 'classnames'
import React from 'react'

const Verso = ({
  isFlipped
}) => {
  return (
    <div className={classnames('verso absolute', {
      'verso--flipped': isFlipped
    })}>
      QSDSQD
    </div>
  )
}

export default Verso
