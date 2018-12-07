class CanvasTools {
  constructor(context) {
    this.context = context
  }

  drawArea(params) {
    // border
    this.context.lineWidth = params.width + 2
    this.context.strokeStyle = 'white'
    this.context.strokeRect(...params.coordinates)
    // Main stroke
    this.context.lineWidth = params.width
    this.context.strokeStyle = params.color
    this.context.strokeRect(...params.coordinates)
    return this
  }

  drawLabel(params) {
    const coordinates = [
      params.parent.coordinates[0],
      params.parent.coordinates[1],
      params.width,
      params.width,
    ]
    // border
    this.context.fillStyle = 'white'
    this.context.fillRect(...this.shift(coordinates))
    // Main stroke
    this.context.fillStyle = params.parent.color
    this.context.fillRect(...coordinates)
    this.context.fillStyle = params.color
    this.context.fillText(params.text, coordinates[0] + 7, coordinates[1] + 14)
    return this
  }

  drawDashed(params) {
    this.context.beginPath()
    this.context.lineWidth = 1
    this.context.setLineDash([params.dash.length, params.dash.space])
    this.context.strokeStyle = params.color
    this.context.strokeRect(...params.coordinates)
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
