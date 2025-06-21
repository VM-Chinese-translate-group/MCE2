ItemEvents.modification(event => {
    event.modify('kubejs:contract', item => {
      item.maxStackSize = 1
      item.burnTime = 20
      item.fireResistant = true
      item.rarity = 'UNCOMMON'
    })
})