import { SPACE_BETWEEN_TWO_IMAGES, DEFAULT_POSITION, DEFAULT_STEP } from '../../_constants'

export const calculatePositionOnXAxis = ({ lastX, maxSteps, newX, step, width }) => {
  const movingRight = lastX > newX
  const movingRatio = width * SPACE_BETWEEN_TWO_IMAGES

  if (movingRight) {
    return step < maxSteps ? lastX - movingRatio : lastX
  } else {
    return step > DEFAULT_STEP ? lastX + movingRatio : DEFAULT_POSITION.x
  }
}

export const calculateStep = ({ lastX, maxSteps, newX, step }) => {
  const movingRight = lastX > newX

  if (movingRight) {
    return step < maxSteps ? step + 1 : maxSteps
  } else {
    return step > DEFAULT_STEP ? step - 1 : DEFAULT_STEP
  }
}
