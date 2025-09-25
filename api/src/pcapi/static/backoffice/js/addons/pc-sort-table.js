/**
 * JS for sorting tables in front
 * This plugin works with the `sortable_column` macro`
 */
class PcSortTable extends PcAddOn {
  static SORTABLE_COLUMN = '.pc-sortable-column'

  bindEvents = () => {
    EventHandler.on(document.body, 'click', PcSortTable.SORTABLE_COLUMN, this.#clicked)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcSortTable.SORTABLE_COLUMN, this.#clicked)
  }

  #getColumnIndex = ($th) => {
    const $tr = $th.closest('tr')
    for (let i = 0; i < $tr.children.length; i++){
      if ($tr.children[i] === $th)
      {
        return i
      }
    }
    console.error('Could not find the index of the column')
  }

  #getOrder = ($th) => {
    const currentOrder = $th.dataset.pcSortTableOrder
    if (currentOrder == 'up'){
      return 'down'
    } else {
      return 'up'
    }
  }

  #getValue = ($tr, index) => {
    return $tr.children[index].dataset.pcSortTableValue
  }
  #orderLines = (index) => {
    return ($a, $b) => {
      return parseFloat(this.#getValue($a, index)) - parseFloat(this.#getValue($b, index))

    }
  }

  #sortTable = ($table, index, order) => {
    const $container = $table.querySelector('tbody') || $table
    const rawLines = $container.getElementsByTagName('tr')
    const lines = []
    const emptyLines = []
    let $header = null
    for (let i = 0; i < rawLines.length; i++) {
      if($container !== $table || !$line.getElementsByTagName('th')){
        const $line = rawLines[i]
        if(!this.#getValue($line, index)){
          emptyLines.push($line)
        } else{
          lines.push($line)
        }
      } else {
        $header = rawLines[i]
      }
    }
    const orderedLines = lines.sort(this.#orderLines(index))
    orderedLines.forEach(($line) => {
      if(order === 'down'){
        $container.append($line)
      }else{
        $container.prepend($line)
      }
    })
    emptyLines.forEach(($line) => {
      $container.append($line)
    })
    if(!!$header){
      $container.prepend($header)
    }
  }

  #resetOrderIcons = ($th) => {
    const tr = $th.closest('tr')
    tr.querySelectorAll('.bi').forEach(($icon) => {
      if($icon.classList.contains('bi-sort-up-alt')){
        $icon.classList.remove('bi-sort-up-alt')
        $icon.classList.add('bi-arrow-down-up')
      } else if($icon.classList.contains('bi-sort-down-alt')){
        $icon.classList.remove('bi-sort-down-alt')
        $icon.classList.add('bi-arrow-down-up')
      }
    })
  }

  #applyOrderIcon = ($th, order) => {
    const $icon = $th.querySelector('.bi')
    $icon.classList.remove('bi-arrow-down-up')
    $icon.classList.add(`bi-sort-${order}-alt`)
  }

  #applySort = ($th) => {
    const index = this.#getColumnIndex($th)
    const order = this.#getOrder($th)
    $th.dataset.pcSortTableOrder = order
    const $table = $th.closest('table')

    $table.classList.add('d-none')
    this.#sortTable($table, index, order)
    this.#resetOrderIcons($th)
    this.#applyOrderIcon($th, order)
    $table.classList.remove('d-none')

  }

  #clicked = (event) =>{
    event.preventDefault()
    const $th = event.target.closest(PcSortTable.SORTABLE_COLUMN)
    this.#applySort($th)
  }
}
