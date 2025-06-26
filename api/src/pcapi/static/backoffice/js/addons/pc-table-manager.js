/**
Manage tables to make them dynamic
 */
class PcTableManager extends PcAddOn {
  static SELECTOR = '.pc-table-manager'
  static DRAGGABLE =  '.pc-table-manager-draggable'
  static VISIBILITY = '.pc-table-manager-toggle-visibility'
  static DISPLAY_ALL = '.pc-table-manager-display-all'
  static DISPLAY_NONE = '.pc-table-manager-display-none'
  static DISPLAY_DEFAULT = '.pc-table-manager-display-default'
  static CLOSE_BUTTON = ".pc-table-manager-close-menu"
  static DROPDOWN_MENU = ".pc-table-manager-dropdown"

  get $tables() {
    return document.querySelectorAll(PcTableManager.SELECTOR)
  }

  #getConfigurationUniqueId = (configurationId) => {
    const baseUrl = window.location.href.toString().split(window.location.host)[1].split('?')[0]
    let configurationUniqueId = 'PcTableManager@' + configurationId + "@"
    baseUrl.split('/').forEach((element) => {
      if (element === ''){}
      else if (!isNaN(element)){
        configurationUniqueId += '/ID'
      } else {
        configurationUniqueId += ('/' + element)
      }
    })
    return configurationUniqueId
  }

  #mergeConfigurations = (configuration, defaultConfiguration) => {
    if (configuration === null){
      return defaultConfiguration
    }
    // create mappings to move from two quadratic expressions to four linear ones
    const columns = configuration.columns.reduce((map, obj) => {
      map[obj.id] = obj;
      return map;
    }, {});

    const defaultColumns = defaultConfiguration.columns.reduce((map, obj) => {
      map[obj.id] = obj;
      return map;
    }, {});
    // add missing columns with default values
    defaultConfiguration.columns.forEach((column) => {
      if(columns[column.id] === undefined) {
        configuration.columns.push(column)
      }
    })
    // remove deleted columns
    const toDelete = []
    if (configuration.columns.length !== defaultConfiguration.columns.length) {
      configuration.columns.forEach((column) => {
      if(defaultColumns[column.id] === undefined) {
        toDelete.push(column)
      }
    })
    toDelete.forEach((column) => {
      configuration.columns.splice(configuration.columns.indexOf(column), 1)
    })
    }
    return configuration
  }

  #initializeTableFromHtml = ($table) => {
    const lines = $table.querySelectorAll("tr")
    const configuration = this.#initializeHeaders($table)
    lines.forEach(($line) => {
      this.#initializeRow(configuration, $line)
    })
    return configuration
  }

  #initializeRow = (configuration, $line) => {
    const cells = $line.querySelectorAll("td")
    if (cells !== null) {
      for (let i=0; i < Math.min(cells.length, configuration.columns.length); i++) {
        cells[i].classList.add(configuration.columns[i].id)
      }
    }
  }

  #initializeHeaders = ($table) => {
    let headerNumber = 0
    const configuration = {
      id: $table.dataset.pcTableManagerId,
      columns: []
    }
    $table.querySelectorAll("th").forEach(($column) => {
      headerNumber++
      const columnConfiguration = {}
      const text_content = $column.textContent.replaceAll(/\n/g, '').trim()
      columnConfiguration.id = text_content.replaceAll(/[^a-zA-Z0-9]/g, '')
      if (columnConfiguration.id === ''){
        columnConfiguration.id = ($column.dataset.pcColumnName || ("default-headerNumber")).replaceAll(/[^a-zA-Z0-9]/g, '')
      }
      columnConfiguration.id = "column-" + columnConfiguration.id
      columnConfiguration.name = $column.dataset.pcColumnName || text_content
      columnConfiguration.display = ($column.dataset.pcDisplayColumn || "true") == "true"
      configuration.columns.push(columnConfiguration)

      $column.classList.add(columnConfiguration.id)
    })
    return configuration
  }
  /** MENU **/
  #initializeMenu = ($table, configuration) => {
    let $container
    if ($table.dataset.pcTableMenuContainerId){
      $container = document.querySelector('#' + $table.dataset.pcTableMenuContainerId)
      $container.classList.add('dropdown')
    } else {
      $container = document.createElement('div')
      $container.classList.add('dropdown')
      $table.before($container)
    }
    this.#createMenu($container, configuration)
    this.#updateMenuContent(configuration)
  }

  #createMenu = ($container, configuration) => {
    const innerHTML = `
        <button class="btn btn-outline-primary-subtle-bg" type="button" data-bs-toggle="dropdown" aria-expanded="false">
          Colonnes
          <i class="bi bi-layout-three-columns ms-2"></i>
        </button>
      <div class="dropdown-menu dropdown-menu-end mt-2 pc-table-manager-dropdown"  data-pc-target-table-id="${configuration.id}">
        <div class="pc-drop-down-header">
          <span>
            Affichez et ordonnez les<br/>colonnes de votre choix.
          </span>
          <button type="button" class="btn btn-outline-primary-subtle-bg border-0 p-2 pc-table-manager-close-menu" data-pc-target-table-id="${configuration.id}" aria-label="Close">
            <i class="bi bi-x-lg fs-5"></i>
          </button>
        </div>
        <div class="pc-table-manager-buttons">
          <a class="link-primary pc-table-manager-display-all" href="" data-pc-target-table-id="${configuration.id}">Tout afficher</a>
          <a class="link-primary pc-table-manager-display-none" href="" data-pc-target-table-id="${configuration.id}">Tout masquer</a>
          <a class="link-primary pc-table-manager-display-default" href="" data-pc-target-table-id="${configuration.id}">Réinitialiser</a></div>
        <ul class="pc-table-manager-draggable" data-pc-target-table-id="${configuration.id}" id="pc-table-manager-menu-container-${configuration.id}" >
        </ul>
      </div>
    `
    $container.innerHTML = innerHTML
  }

  #updateMenuContent = (configuration) => {
    const $container = document.querySelector(`#pc-table-manager-menu-container-${configuration.id}`)
    const elements = []
    configuration.columns.forEach((column) => {
      elements.push(
        `
          <li class="dropdown-item" draggable="true" data-pc-target-column-id="${column.id}">
            <div>
              <input type="checkbox" class="form-check-input pc-table-manager-toggle-visibility" data-pc-target-table-id="${configuration.id}" data-pc-target-column-id="${column.id}"  ${column.display?'checked':''}/>
              <span class="pc-column-title${column.display?' ':' pc-table-manager-disabled'}">${column.name}</span>
            </div>
            <i class="bi bi-grip-vertical${column.display?' ':' pc-table-manager-disabled'}"></i>
          </li>
        `
      )
    })
    $container.innerHTML = elements.join("\n")
  }

  #stopPropagation = (event) => {
    event.stopPropagation()
  }

  #onCloseMenuClick = (event) => {
    const configurationId = event.target.closest('.pc-table-manager-close-menu').dataset.pcTargetTableId
    const $menu = document.querySelector(`#pc-table-manager-menu-container-${configurationId}`).closest('.show')
    $menu.classList.remove('show')
  }

  #onVisibilityToggleClick = (event) => {
    event.stopPropagation()
    const configuration = this.#getConfigurationForEdit(event.target.dataset.pcTargetTableId)
    const columnId = event.target.dataset.pcTargetColumnId
    configuration.columns.forEach((column) => {

      if (column.id == columnId){
        column.display = event.target.checked
      }
    })
    this.applyConfiguration(configuration)
  }

  #onDisplayAllClick = (event) => {
    event.stopPropagation()
    event.preventDefault()
    const configuration = this.#getConfigurationForEdit(event.target.dataset.pcTargetTableId)
    configuration.columns.forEach((column) => {
      column.display = true
    })
    this.applyConfiguration(configuration)
  }

  #onDisplayNoneClick = (event) => {
    event.stopPropagation()
    event.preventDefault()
    const configuration = this.#getConfigurationForEdit(event.target.dataset.pcTargetTableId)
    configuration.columns.forEach((column) => {
      column.display = false
    })
    this.applyConfiguration(configuration)
  }

  #onDisplayDefaultClick = (event) => {
    event.stopPropagation()
    event.preventDefault()
    this.restoreDefaultConfiguration(event.target.dataset.pcTargetTableId)
  }

  /** DRAG AND DROP **/
  #getValidTarget = ($element) => {
    if($element.tagName === 'BODY'){
      return null
    }
    else if($element.tagName === 'LI' && $element.classList.contains('dropdown-item')){
      return $element
    }
    else{
      return this.#getValidTarget($element.parentElement)
    }
  }

  #resetDropTarget = ($element) => {
    $element.classList.remove('pc-table-manager-target')
    $element.style.marginTop = ''
    $element.style.marginBottom = ''
    delete $element.position
  }

  #onDragStart = (event) => {
    // on a setTimeout to do it once the dragstart event is finished
    event.target.parentElement.dataset.pcTableManagerDraggableHeight = event.target.getBoundingClientRect().height
    setTimeout(() => {
      event.target.classList.add('d-none')
      event.target.parentElement.appendChild(event.target) // small hack to avoid graphical glitch
    }, 0)
  }

  #onDragEnd = (event) => {
    // on a setTimeout to do it once the dragend event is finished
    const $parent = event.target.parentElement
    setTimeout(() => {event.target.classList.remove('d-none')}, 0)
    delete event.target.parentElement.dataset.pcTableManagerDraggableHeight
    const $dropTarget = $parent.querySelector('.pc-table-manager-target')
    if($dropTarget !== null) {
      if ($dropTarget.dataset.position === 'after') {
        $dropTarget.before(event.target)
      } else {
        $dropTarget.after(event.target)
      }
      this.#resetDropTarget($dropTarget)
    }
    //compute and render new table
    const configuration = this.#getConfigurationForEdit($parent.dataset.pcTargetTableId)
    const columnsMap = configuration.columns.reduce((map, obj) => {
      map[obj.id] = obj;
      return map;
    }, {});
    const newColumns = []
    for(let i = 0; i < $parent.children.length; i++){
      newColumns.push(columnsMap[$parent.children[i].dataset.pcTargetColumnId])
    }
    configuration.columns = newColumns
    this.applyConfiguration(configuration)
  }

  #onDragOver = (event) => {
    const $target = this.#getValidTarget(event.target)
    if($target !== null) {
      const targetBox = $target.getBoundingClientRect()
      const position = (event.clientY - targetBox.top) / targetBox.height
      $target.classList.add('pc-table-manager-target')
      if (position < 0.5) {
        // we are on the top part of the target
        if($target.style.marginTop == '') {
          //manage a clean spacing when moving the element
          const rawPadding = window.getComputedStyle($target, null).getPropertyValue('margin-top')
          let margin = parseInt(rawPadding.replace(/[^0-9]/g, ''))
          margin += parseInt($target.parentElement.dataset.pcTableManagerDraggableHeight)
          margin += 8 // old margin
          $target.style.marginTop = margin + 'px'
          $target.style.marginBottom = ''
        }
        $target.dataset.position = 'after'
      } else {
        // we are on the bottom part of the target
        if($target.style.marginBottom == '') {
          //manage a clean spacing when moving the element
          const rawPadding = window.getComputedStyle($target, null).getPropertyValue('margin-bottom')
          let margin = parseInt(rawPadding.replace(/[^0-9]/g, ''))
          margin += parseInt($target.parentElement.dataset.pcTableManagerDraggableHeight)
          margin += 8 // old margin
          $target.style.marginBottom = margin + 'px'
          $target.style.marginTop = ''
        }
        $target.dataset.position = 'before'
      }
      $target.parentElement.querySelectorAll('.pc-table-manager-target').forEach(($element) => {
        if ($element !== $target) {
          this.#resetDropTarget($element)
        }
      })
    }
  }
  /** END DRAG AND DROP **/
  #applyConfigurationOnTable = (configuration) => {
    const previousConfiguration = this.configurations[configuration.id]
    const $table = document.querySelector(`table[data-pc-table-manager-id="${configuration.id}"]`)

    if(! this.#needUpdate(previousConfiguration, configuration)){
      // fast path to not blink the table if nothing changed
      $table.classList.remove('d-none')
      this.saveConfiguration(configuration)
      this.configurations[configuration.id] = configuration
      return
    }

    $table.classList.add('d-none')
    $table.querySelectorAll("tr").forEach(($line) => {
      this.#applyConfigurationOnLine(configuration, $line)
    })
    $table.classList.remove('d-none')
  }

  #applyConfigurationOnLine = (configuration, $line) => {
    const oldConfigurationMap = {}
    // ignore lines with too few colonnes for pages like bookings
    if($line.children.length >= (configuration.columns.length * 0.5)) {
      configuration.columns.forEach((columnConfiguration) => {
        // retrieve cell to move/update
        let $cell
        if (oldConfigurationMap[columnConfiguration.id] === undefined) {
          for(let i=0; i < $line.children.length; i++){
            if ($line.children[i].classList.contains(columnConfiguration.id)){
              $cell = $line.children[i]
              oldConfigurationMap[columnConfiguration.id] = i
              break
            }
          }
        } else {
          $cell = $line.children[oldConfigurationMap[columnConfiguration.id]]
        }
        if ($cell){
          // apply configuration
          if(columnConfiguration.display){
            $cell.classList.remove('d-none')
            $line.appendChild($cell)
          } else {
            $cell.classList.add('d-none')
          }
        }
      })
    }
  }

  #getConfigurationForEdit = (id) => {
    return structuredClone(this.configurations[id])
  }

  #needUpdate = (previousConfiguration, configuration) => {
    for(let i=0; i<previousConfiguration.columns.length; i++){
      if (
        previousConfiguration.columns[i].id != configuration.columns[i].id
        || previousConfiguration.columns[i].display != configuration.columns[i].display
      ){
        return true
      }
    }
    return false
  }

  #applyConfigurationOnLoadedLines = (event) => {
    if (!event.detail.isError) {
      let $table = event.target.closest(`table${PcTableManager.SELECTOR}`)

      if (!!$table) {
        // replace default htmx swap behaviour
        event.detail.shouldSwap = false
        // create a temporary table to place rows received from server response
        const tempTable = document.createElement("table")
        const tableId = $table.dataset.pcTableManagerId
        const configuration = this.configurations[tableId]
        const defaultConfiguration = this.defaultConfigurations[tableId]
        tempTable.innerHTML = event.detail.serverResponse
        const $newLines = tempTable.querySelectorAll("tr")
        // re-arrange each line's columns to fit applied filters
        $newLines.forEach(($newLine) => {
          this.#initializeRow(defaultConfiguration, $newLine)
          this.#applyConfigurationOnLine(configuration, $newLine)
          htmx.swap(`tr#${$newLine.id}`, $newLine.outerHTML, {swapStyle: "outerHTML"})
        })
        // re-init table selection checkboxes and unselect them all
        this.app.addons.PcTableMultiSelectId.refreshTableState($table)
        this.app.addons.PcTableMultiSelectId.batchSelect($table, false)
      }
    }
  }

  initialize = () => {
    this.configurations = {}
    this.defaultConfigurations = {}
    this.$tables.forEach(($table) => {
      const defaultConfiguration = this.#initializeTableFromHtml($table)
      this.defaultConfigurations[defaultConfiguration.id] = defaultConfiguration
      this.configurations[defaultConfiguration.id] = defaultConfiguration
      const oldConfiguration = this.getConfiguration(defaultConfiguration.id)
      const configuration = this.#mergeConfigurations(oldConfiguration, defaultConfiguration)
      this.#initializeMenu($table, configuration)
      this.applyConfiguration(configuration)
    })
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'dragstart', PcTableManager.DRAGGABLE, this.#onDragStart)
    EventHandler.on(document.body, 'dragend', PcTableManager.DRAGGABLE, this.#onDragEnd)
    EventHandler.on(document.body, 'dragover', PcTableManager.DRAGGABLE, this.#onDragOver)
    EventHandler.on(document.body, 'click', PcTableManager.VISIBILITY, this.#onVisibilityToggleClick)
    EventHandler.on(document.body, 'click', PcTableManager.DISPLAY_ALL, this.#onDisplayAllClick)
    EventHandler.on(document.body, 'click', PcTableManager.DISPLAY_NONE, this.#onDisplayNoneClick)
    EventHandler.on(document.body, 'click', PcTableManager.DISPLAY_DEFAULT, this.#onDisplayDefaultClick)
    EventHandler.on(document.body, 'click', PcTableManager.CLOSE_BUTTON, this.#onCloseMenuClick)
    EventHandler.on(document.body, 'click', PcTableManager.DROPDOWN_MENU, this.#stopPropagation)
    EventHandler.on(document.body, "htmx:beforeSwap", this.#applyConfigurationOnLoadedLines)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'dragstart', PcTableManager.DRAGGABLE, this.#onDragStart)
    EventHandler.off(document.body, 'dragend', PcTableManager.DRAGGABLE, this.#onDragEnd)
    EventHandler.off(document.body, 'dragover', PcTableManager.DRAGGABLE, this.#onDragOver)
    EventHandler.off(document.body, 'click', PcTableManager.VISIBILITY, this.#onVisibilityToggleClick)
    EventHandler.off(document.body, 'click', PcTableManager.DISPLAY_ALL, this.#onDisplayAllClick)
    EventHandler.off(document.body, 'click', PcTableManager.DISPLAY_NONE, this.#onDisplayNoneClick)
    EventHandler.off(document.body, 'click', PcTableManager.DISPLAY_DEFAULT, this.#onDisplayDefaultClick)
    EventHandler.off(document.body, 'click', PcTableManager.CLOSE_BUTTON, this.#onCloseMenuClick)
    EventHandler.off(document.body, 'click', PcTableManager.DROPDOWN_MENU, this.#stopPropagation)
    EventHandler.off(document.body, "htmx:beforeSwap", this.#applyConfigurationOnLoadedLines)
  }

  applyConfiguration = (configuration) => {
    this.#applyConfigurationOnTable(configuration)
    this.#updateMenuContent(configuration)
    this.saveConfiguration(configuration)
    this.configurations[configuration.id] = configuration
  }

  saveConfiguration = (configuration) => {
    localStorage.setItem(this.#getConfigurationUniqueId(configuration.id), JSON.stringify(configuration))
  }

  getConfiguration = (configurationId) => {
    const rawConfiguration = localStorage.getItem(this.#getConfigurationUniqueId(configurationId))
    if(rawConfiguration){
      return JSON.parse(rawConfiguration)
    }
    return null
  }

  restoreDefaultConfiguration = (configurationId) => {
    const configuration = this.defaultConfigurations[configurationId]
    if(configuration){
      this.applyConfiguration(configuration)
    }
  }
}
