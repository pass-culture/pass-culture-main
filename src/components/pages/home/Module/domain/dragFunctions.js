export const DEFAULT_STEP = 1
export const DEFAULT_POSITION = 0

export const calculatePositionX = ({
                                     lastX,
                                     maxSteps,
                                     newX,
                                     step,
                                     width
                                   }) => {
  const movingRight = lastX > newX
  const movingRatio = width * 1.035

  if (movingRight) {
    if (step < maxSteps) {
      return lastX - movingRatio
    }
    return lastX
  } else {
    if (step > DEFAULT_STEP) {
      return lastX + movingRatio
    }
    return DEFAULT_POSITION
  }
}

export const calculateStep = ({ lastX, maxSteps, newX, step }) => {
  const movingRight = lastX > newX

  if (movingRight) {
    if (step < maxSteps) {
      return step + 1
    }
    return maxSteps
  } else {
    if (step > DEFAULT_STEP) {
      return step - 1
    }
    return DEFAULT_STEP
  }
}
