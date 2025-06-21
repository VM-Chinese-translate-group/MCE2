
StartupEvents.registry('item', event => {
    event.create('mcejaffa')
        .displayName('§5Happy Welcome Jaffa')
        .food(food => {
            food.hunger(30)
            food.saturation(0.5)
            food.effect('alexscaves:sugar_rush', 150, 0, 1.0)
        })
})
