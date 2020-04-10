import React, { useState } from 'react'
import PropTypes from 'prop-types'

import Icon from '../../layout/Icon/Icon'
import FirstTutorial from './FirstTutorial/FirstTutorial'
import SecondTutorial from './SecondTutorial/SecondTutorial'
import ThirdTutorial from './ThirdTutorial/ThirdTutorial'
import SliderPoints from './SliderPoints/SliderPoints'
import DraggableTutorial from './DraggableTutorial/DraggableTutorial'
import EnteringSides from './animationsEnteringSides/EnteringSides'

const Tutorials = ({ history }) => {
  const tutorials = [FirstTutorial, SecondTutorial, ThirdTutorial]
  const lastTutorialStep = tutorials.length - 1

  let [step, setStep] = useState(0)
  let [previousStep, setPreviousStep] = useState(-1)

  function handleGoNext() {
    if (step === lastTutorialStep) {
      history.push('/decouverte')
    } else {
      setPreviousStep(step)
      setStep(step + 1)
    }
  }

  function handleGoPrevious() {
    setPreviousStep(step)
    setStep(step - 1)
  }

  function tutorialToDisplay() {
    const enteringSide = previousStep < step ? EnteringSides.right : EnteringSides.left

    if (step === 0) {
      return <FirstTutorial enteringSide={enteringSide} />
    }

    if (step === 1) {
      return <SecondTutorial enteringSide={enteringSide} />
    }

    if (step === 2) {
      return <ThirdTutorial enteringSide={enteringSide} />
    }
  }

  return (
    <main className="tutorials">
      <DraggableTutorial
        handleGoNext={handleGoNext}
        handleGoPrevious={handleGoPrevious}
        step={step}
      >
        {tutorialToDisplay()}
      </DraggableTutorial>
      {step > 0 && (
        <button
          className="previous-arrow"
          onClick={handleGoPrevious}
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
        onClick={handleGoNext}
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
          maxStep={tutorials.length}
        />
      </div>
    </main>
  )
}

Tutorials.propTypes = {
  history: PropTypes.shape().isRequired,
}

export default Tutorials
