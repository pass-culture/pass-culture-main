import { SPACE_BETWEEN_TWO_IMAGES, DEFAULT_POSITION, DEFAULT_STEP } from '../../_constants'

export const calculatePositionOnXAxis = ({
  lastPositionOnXAxis,
  maxSteps,
  newPositionOnXAxis,
  step,
  width,
}) => {
  const movingRight = lastPositionOnXAxis > newPositionOnXAxis
  const movingRatio = width * SPACE_BETWEEN_TWO_IMAGES

  if (movingRight) {
    return step < maxSteps ? lastPositionOnXAxis - movingRatio : lastPositionOnXAxis
  } else {
    return step > DEFAULT_STEP ? lastPositionOnXAxis + movingRatio : DEFAULT_POSITION.x
  }
}

export const calculateStep = ({ lastPositionOnXAxis, maxSteps, newPositionOnXAxis, step }) => {
  const movingRight = lastPositionOnXAxis > newPositionOnXAxis

  if (movingRight) {
    return step < maxSteps ? step + 1 : maxSteps
  } else {
    return step > DEFAULT_STEP ? step - 1 : DEFAULT_STEP
  }
}
