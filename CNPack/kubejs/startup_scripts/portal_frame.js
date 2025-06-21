StartupEvents.registry("block", (event) => {
    event.create("ancient_portal_stone") 
    .displayName("Ancient Portal Stone") 
    .material("stone") 
    .hardness(55.0) 
	.unbreakable()
    .resistance(50.0) // Set resistance (to explosions, etc)
    .requiresTool(true) // Requires a tool or it won't drop (see tags below)
})