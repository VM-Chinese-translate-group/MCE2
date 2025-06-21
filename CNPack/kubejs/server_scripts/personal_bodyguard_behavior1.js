ItemEvents.rightClicked(event => {
    const { item, player, server } = event;
    if (!server || item.id !== 'kubejs:mossy_letter') return;

    const name = player.username;

    
    player.getCooldowns().addCooldown('kubejs:mossy_letter', 9500);


    server.runCommand(`tellraw ${name} {"text":"Your personal bodyguard has arrived! ","italic":true,"color":"dark_green"}`);
    server.runCommand(`execute at ${name} run playsound minecraft:entity.wither.spawn ambient ${name}`);
    server.runCommand(`execute at ${name} run particle create:soul ~ ~ ~`);


    player.potionEffects.add('minecraft:glowing', 1000, 0);


    const weightedEntitiess = [
        { id: 'goety_cataclysm:coralssus', weight: 1 },

    ];


    const totalWeight = weightedEntitiess.reduce((sum, entity) => sum + entity.weight, 0);
    let rand = Math.random() * totalWeight;
    let selectedEntity = null;

    for (const entity of weightedEntitiess) {
        rand -= entity.weight;
        if (rand <= 0) {
            selectedEntity = entity.id;
            break;
        }
    }

    if (selectedEntity) {
        let entityTag = `temp_${Date.now()}`;

       
        server.runCommand(`execute at ${name} run summon ${selectedEntity} ~ ~5 ~5 {DeathLootTable:"minecraft:empty"}`);

        
        server.runCommand(`execute at ${name} run tag @e[type=${selectedEntity},distance=..50,limit=1,sort=nearest] add ${entityTag}`);


        server.scheduleInTicks(1000, () => {
            server.runCommand(`execute as @e[tag=${entityTag}] at @s run particle minecraft:squid_ink ~ ~1 ~ 0.5 1 0.5 0.01 100 force`);
            server.runCommand(`kill @e[tag=${entityTag}]`);
        });
    }
    
});
