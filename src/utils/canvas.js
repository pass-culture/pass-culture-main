function getScaledCoordinates(coordinates) {
  const scaledCoordinates = [...coordinates]
  const dpr = window.devicePixelRatio
  scaledCoordinates[0] = dpr * coordinates[0]
  scaledCoordinates[1] = dpr * coordinates[1]
  scaledCoordinates[2] = dpr * coordinates[2]
  scaledCoordinates[3] = dpr * coordinates[3]
  return scaledCoordinates
}

function getScaledFont(params) {
  return `${params.fontWeight} ${window.devicePixelRatio * params.fontSize}px ${params.fontFamily}`
}

function getScaledTextCoordinates(coordinates) {
  const dpr = window.devicePixelRatio
  return [dpr * (coordinates[0] + 7), dpr * (coordinates[1] + 14)]
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

  drawLabel(params) {
    const coordinates = [
      params.parent.coordinates[0],
      params.parent.coordinates[1],
      params.width,
      params.width,
    ]
    // scale
    const scaledCoordinates = getScaledCoordinates(coordinates)
    const scaledFont = getScaledFont(params)
    const scaledTextCoordinates = getScaledTextCoordinates(coordinates)
    // border
    this.context.fillStyle = 'white'
    this.context.fillRect(...this.shift(scaledCoordinates))
    // Main stroke
    this.context.fillStyle = params.parent.color
    this.context.fillRect(...scaledCoordinates)
    this.context.fillStyle = params.color
    this.context.font = scaledFont
    this.context.fillText(params.text, ...scaledTextCoordinates)

    return this
  }

  drawDashed(params) {
    const scaledCoordinates = getScaledCoordinates(params.coordinates)
    this.context.beginPath()
    this.context.lineWidth = 1
    this.context.setLineDash([params.dash.length, params.dash.space])
    this.context.strokeStyle = params.color
    this.context.strokeRect(...scaledCoordinates)
    this.context.setLineDash([0, 0])
    return this
  }

  shift(coords) {
    const shiftedCoords = Array.from(coords)
    shiftedCoords[0] += 0.5
    shiftedCoords[1] += 0.5

    return shiftedCoords
  }
}

export default CanvasTools
