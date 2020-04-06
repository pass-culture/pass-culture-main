import React, { useState } from 'react'
import PropTypes from 'prop-types'

import FirstTutorial from './FirstTutorial/FirstTutorial'
import Icon from '../../layout/Icon/Icon'
import SecondTutorial from './SecondTutorial/SecondTutorial'
import ThirdTutorial from './ThirdTutorial/ThirdTutorial'
import SliderPoints from './SliderPoints/SliderPoints'

const Tutorials = ({ history }) => {

  const tutorials = [
    <FirstTutorial />,
    <SecondTutorial />,
    <ThirdTutorial />
  ]

  const lastTutorialStep = tutorials.length -1

  let [step, setStep] = useState(0)

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
      {step > 0 && (
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
      <div className="slider-points">
        <SliderPoints
          currentStep={step}
          elements={tutorials}
        />
      </div>
    </main>
  )
}

Tutorials.propTypes = {
  history: PropTypes.shape().isRequired,
}

export default Tutorials
