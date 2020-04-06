import React, { useState } from 'react'
import PropTypes from 'prop-types'

import FirstTutorial from './FirstTutorial/FirstTutorial'
import Icon from '../../layout/Icon/Icon'
import SecondTutorial from './SecondTutorial/SecondTutorial'
import ThirdTutorial from './ThirdTutorial/ThirdTutorial'

const Tutorials = ({ history }) => {
  const tutorials = {
    1: <FirstTutorial />,
    2: <SecondTutorial />,
    3: <ThirdTutorial />,
  }

  const lastTutorialStep = Object.keys(tutorials).length

  let [step, setStep] = useState(1)

  function handleClickNext() {
    if (step === lastTutorialStep) {
      history.push('/decouverte')
    }

    setStep(step + 1)
  }

  function handleClickPrevious() {
    setStep(step - 1)
  }

  return (
    <main className="tutorials">
      {tutorials[step]}
      {step > 1 && (
        <button
          className="previous-arrow"
          onClick={handleClickPrevious}
          type="button"
        >
          <Icon
            alt="Précédent"
            svg="icon-arrow"
          />
        </button>
      )}
      <button
        className="next-arrow"
        onClick={handleClickNext}
        type="button"
      >
        <Icon
          alt="Suivant"
          svg="icon-arrow"
        />
      </button>
    </main>
  )
}

Tutorials.propTypes = {
  history: PropTypes.shape().isRequired,
}

export default Tutorials
