StartupEvents.registry('item', event => {
    event.create('s_soup')
        .displayName('§eSculptor Soup')
        .food(food => {
            food.hunger(30)
            food.saturation(0.5)
            food.effect('mowziesmobs:geomancy', 350, 0, 1.0)
        })
})
