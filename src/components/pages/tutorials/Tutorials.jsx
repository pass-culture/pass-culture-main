import React, { useState } from 'react'
import PropTypes from 'prop-types'

import FirstTutorial from './FirstTutorial/FirstTutorial'
import Icon from '../../layout/Icon/Icon'
import SecondTutorial from './SecondTutorial/SecondTutorial'
import ThirdTutorial from './ThirdTutorial/ThirdTutorial'

const Tutorials = ({ history }) => {
  let [displayFirstTutorial, setDisplayFirstTuto] = useState(true)
  let [displaySecondTutorial, setDisplaySecondTuto] = useState(false)
  let [displayThirdTutorial, setDisplayThirdTuto] = useState(false)

  function handleClickNext() {
    if (displayThirdTutorial) {
      history.push('/decouverte')
    }

    if (displaySecondTutorial) {
      setDisplaySecondTuto(false)
      setDisplayThirdTuto(true)
    } else {
      setDisplayFirstTuto(false)
      setDisplaySecondTuto(true)
    }
  }

  function handleClickPrevious() {
    if (displayThirdTutorial) {
      setDisplaySecondTuto(true)
      setDisplayThirdTuto(false)
    } else {
      setDisplaySecondTuto(false)
      setDisplayFirstTuto(true)
    }
  }

  return (
    <main className="tutorials">
      {displayFirstTutorial && <FirstTutorial />}
      {displaySecondTutorial && <SecondTutorial />}
      {displayThirdTutorial && <ThirdTutorial />}
      {(displaySecondTutorial || displayThirdTutorial) && (
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
