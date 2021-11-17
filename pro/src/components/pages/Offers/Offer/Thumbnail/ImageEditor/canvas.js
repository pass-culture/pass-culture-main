/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 */

function getScaledCoordinates(coordinates) {
  const scaledCoordinates = [...coordinates]
  const dpr = window.devicePixelRatio
  scaledCoordinates[0] = dpr * coordinates[0]
  scaledCoordinates[1] = dpr * coordinates[1]
  scaledCoordinates[2] = dpr * coordinates[2]
  scaledCoordinates[3] = dpr * coordinates[3]
  return scaledCoordinates
}

class CanvasTools {
  constructor(context) {
    this.context = context
  }

  drawArea(params) {
    // scale
    const scaledCoordinates = getScaledCoordinates(params.coordinates)
    // border
    this.context.lineWidth = params.width + 2
    this.context.strokeStyle = 'white'
    this.context.strokeRect(...scaledCoordinates)
    // Main stroke
    this.context.lineWidth = params.width
    this.context.strokeStyle = params.color
    this.context.strokeRect(...scaledCoordinates)
    return this
  }
}

export default CanvasTools
