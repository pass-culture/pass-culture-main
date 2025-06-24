/* istanbul ignore file: DEBT, TO FIX */

type Coordinates = [number, number, number, number]

function getScaledCoordinates(coordinates: Coordinates): Coordinates {
  const dpr = window.devicePixelRatio
  return [
    dpr * coordinates[0],
    dpr * coordinates[1],
    dpr * coordinates[2],
    dpr * coordinates[3],
  ]
}
export class CanvasTools {
  context: CanvasRenderingContext2D

  constructor(context: CanvasRenderingContext2D) {
    this.context = context
  }

  drawArea(params: { width: number; color: string; coordinates: Coordinates }) {
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
